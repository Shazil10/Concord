"""Concord agent: run one trade through the 12-step verification pipeline."""

from __future__ import annotations

import json
import uuid

import prismtrace

from concord import tools, llm
from concord.config import CONCORD_MODEL, DEMO_DATE
from concord.tracing import get_client, step


def run_trade(trade_id: str, version: str) -> dict:
    """Run the full pipeline for one trade. Returns the result dict.

    version is "v1" or "v2". v1 has deliberate bugs (stale SSI, crash on
    missing counterparty). v2 has the fixes.
    """
    session_id = f"{version}-{trade_id}-{uuid.uuid4().hex[:8]}"
    pt = get_client()
    steps: list[dict] = []
    all_breaks: list[dict] = []
    total_tokens = {"input": 0, "output": 0}
    missing_cpty = False
    error_out = None

    def _track_tokens(result: dict | None) -> None:
        if result and isinstance(result, dict) and "tokens" in result:
            t = result["tokens"]
            total_tokens["input"] += t.get("input", 0) or 0
            total_tokens["output"] += t.get("output", 0) or 0

    with prismtrace.session(session_id):
        # ── Step 1: load_trade ───────────────────────────────────────
        s1 = step("load_trade", f"trade_id={trade_id}",
                   lambda: tools.load_trade(trade_id, version))
        steps.append(s1["step"])
        if s1.get("error"):
            error_out = s1["error"]
        trade = s1["result"]["trade"] if s1["result"] else {}
        email_text = s1["result"]["email"] if s1["result"] else None

        counterparty = trade.get("counterparty", "")
        product = trade.get("product", "")
        settle_date = trade.get("settle_date", "")

        # ── Step 2: parse_our_confirmation (LLM) ────────────────────
        s2 = step("parse_our_confirmation", f"trade_id={trade_id}",
                   lambda: tools.parse_our_confirmation(trade_id), is_llm=True)
        steps.append(s2["step"])
        _track_tokens(s2["result"])
        our_parsed = s2["result"]["parsed"] if s2["result"] else {}

        # ── Step 3: parse_counterparty_confirmation (LLM) ───────────
        s3 = step("parse_counterparty_confirmation", f"trade_id={trade_id}, version={version}",
                   lambda: tools.parse_counterparty_confirmation(trade_id, version), is_llm=True)
        steps.append(s3["step"])
        if s3.get("error"):
            # v1 crash on missing counterparty
            error_out = s3["error"]
            missing_cpty = True
            cpty_parsed = None
        elif s3["result"] and s3["result"].get("missing"):
            missing_cpty = True
            cpty_parsed = None
        else:
            _track_tokens(s3["result"])
            cpty_parsed = s3["result"]["parsed"] if s3["result"] else None

        # If v1 crashes, stop here
        if error_out and version == "v1":
            _send_trajectory(pt, steps, session_id, version, trade_id, product, "error")
            raise error_out

        # ── Step 4: get_custodian_status ─────────────────────────────
        s4 = step("get_custodian_status", f"trade_id={trade_id}",
                   lambda: tools.get_custodian_status(trade_id))
        steps.append(s4["step"])

        # ── Step 5: lookup_ssi_registry ──────────────────────────────
        pay_ccy = trade.get("ccy_sold") or trade.get("ccy_bought") or "USD"
        s5 = step("lookup_ssi_registry",
                   f"counterparty={counterparty}, ccy={pay_ccy}, settle={settle_date}, ver={version}",
                   lambda: tools.lookup_ssi_registry(counterparty, pay_ccy, settle_date, version))
        steps.append(s5["step"])
        registry_instructions = s5["result"]["instructions"] if s5["result"] else []

        # ── Step 6: resolve_bank_branch ──────────────────────────────
        our_pay_code = our_parsed.get("pay_bank_code", "")
        s6 = step("resolve_bank_branch", f"bank_code={our_pay_code}",
                   lambda: tools.resolve_bank_branch(our_pay_code))
        steps.append(s6["step"])

        # ── Step 7: check_entity_account ─────────────────────────────
        our_pay_acct = our_parsed.get("pay_account") or ""
        # Skip entity check if we have no pay account to check (e.g. bond SELL)
        if not our_pay_acct and not our_pay_code:
            s7 = step("check_entity_account", "skipped — no pay instruction on our side",
                       lambda: {"ok": True, "breaks": [], "note": "No pay instruction"})
        else:
            s7 = step("check_entity_account",
                       f"account={our_pay_acct}, code={our_pay_code}",
                       lambda: tools.check_entity_account(
                           our_pay_acct,
                           our_pay_code,
                           registry_instructions,
                       ))
        steps.append(s7["step"])
        if s7["result"] and not s7["result"]["ok"]:
            all_breaks.extend(s7["result"].get("breaks", []))

        # ── Step 8: cross_match_sides ────────────────────────────────
        if cpty_parsed:
            s8 = step("cross_match_sides", f"our vs cpty for {trade_id}",
                       lambda: tools.cross_match_sides(our_parsed, cpty_parsed))
        else:
            s8 = step("cross_match_sides", f"skipped — no counterparty confirm",
                       lambda: {"ok": True, "breaks": [], "note": "No cpty confirmation"})
        steps.append(s8["step"])
        if s8["result"] and not s8["result"]["ok"]:
            all_breaks.extend(s8["result"].get("breaks", []))

        # ── Step 9: compare_economics ────────────────────────────────
        s9 = step("compare_economics", f"trade vs confirmations for {trade_id}",
                   lambda: tools.compare_economics(trade, our_parsed, cpty_parsed))
        steps.append(s9["step"])
        if s9["result"] and not s9["result"]["ok"]:
            all_breaks.extend(s9["result"].get("breaks", []))

        # ── Step 10: estimate_fail_cost ──────────────────────────────
        s10 = step("estimate_fail_cost", f"trade={trade_id}, demo_date={DEMO_DATE}",
                    lambda: tools.estimate_fail_cost(trade, DEMO_DATE))
        steps.append(s10["step"])

        # ── Step 11: decide ──────────────────────────────────────────
        s11 = step("decide", f"{len(all_breaks)} breaks, missing_cpty={missing_cpty}",
                    lambda: tools.decide(all_breaks, missing_cpty))
        steps.append(s11["step"])
        decision_result = s11["result"] if s11["result"] else {"decision": "Hold", "reason": "Error"}
        decision = decision_result["decision"]

        # ── Step 12: draft_message (LLM) ─────────────────────────────
        if decision == "Release" and not all_breaks and not missing_cpty:
            s12 = step("draft_message", "clean release",
                       lambda: {"data": {"message": "Matched. Ready to release.", "recipient": "internal"},
                                "tokens": {"input": 0, "output": 0}})
        else:
            explanation_result = llm.explain_breaks(trade, all_breaks, email_text)
            _track_tokens(explanation_result)
            expl = explanation_result["data"]
            fault = expl.get("fault", "unknown")
            urgency = expl.get("urgency", "email")
            explanation_text = expl.get("explanation", "")

            def _do_draft():
                return llm.draft_message(trade, all_breaks, fault, urgency, explanation_text)
            s12 = step("draft_message", f"fault={fault}, urgency={urgency}", _do_draft, is_llm=True)
            _track_tokens(s12["result"])

        steps.append(s12["step"])
        draft_data = s12["result"]["data"] if s12["result"] else {"message": "", "recipient": ""}

    # Build final result
    outcome = "correct" if decision else "error"
    if decision == "Release" and all_breaks:
        outcome = "wrong_release"

    # For stale_ssi trades in v1, check if we wrongly released
    # (v1 won't see the breaks because it reads the old snapshot)
    final_status = "success" if not error_out else "error"

    result = {
        "trade_id": trade_id,
        "product": product,
        "counterparty": counterparty,
        "settle_date": settle_date,
        "version": version,
        "decision": decision,
        "reason": decision_result.get("reason", ""),
        "fault": draft_data.get("recipient", "") if decision == "Hold" else "none",
        "urgency": "none",
        "breaks": all_breaks,
        "draft_message": draft_data.get("message", ""),
        "summary": decision_result.get("reason", ""),
        "fail_cost": s10["result"] if s10["result"] else {},
        "total_tokens": total_tokens,
        "session_id": session_id,
    }

    # Extract fault and urgency from LLM explanation if we had breaks
    if decision != "Release" and not missing_cpty and s12["result"]:
        try:
            result["fault"] = expl.get("fault", "unknown")
            result["urgency"] = expl.get("urgency", "email")
        except NameError:
            pass

    if missing_cpty:
        result["fault"] = "counterparty"
        result["urgency"] = "call" if settle_date <= DEMO_DATE else "email"
        result["reason"] = "Missing counterparty confirmation — chase required"

    _send_trajectory(pt, steps, session_id, version, trade_id, product, final_status)
    return result


def _send_trajectory(
    pt, steps, session_id, version, trade_id, product, final_status
):
    """Submit the trajectory and a summary trace to PRISM."""
    with prismtrace.session(session_id):
        pt.submit_trajectory(
            steps=[s for s in steps],
            agent_name="concord",
            agent_id="concord",
            model=CONCORD_MODEL,
            final_status=final_status,
        )

        decision = "unknown"
        for s in reversed(steps):
            if s["label"] == "decide" and "Release" in s.get("output_summary", ""):
                decision = "Release"
                break
            elif s["label"] == "decide":
                decision = "Hold"
                break

        pt.trace_llm(
            model=CONCORD_MODEL,
            agent_name="concord",
            agent_id="concord",
            input_messages=[{"role": "user", "content": f"Verify trade {trade_id}"}],
            output=f"{decision} — {final_status}",
            latency_ms=sum(s.get("duration_ms", 0) for s in steps),
            metadata={
                "version": version,
                "trade_id": trade_id,
                "product": product,
                "decision": decision,
                "final_status": final_status,
                "step_count": len(steps),
            },
        )
