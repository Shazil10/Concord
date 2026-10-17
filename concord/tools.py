"""The 12 deterministic tools that form Concord's pipeline.

Each tool returns a dict with at minimum {"ok": bool}. Tools that find
mismatches include a "breaks" list. The agent calls them in order.
"""

from __future__ import annotations

from typing import Optional

from concord import data, llm


# ── 1. load_trade ──────────────────────────────────────────────────────

def load_trade(trade_id: str, version: str) -> dict:
    trade = data.load_trade(trade_id)
    email = data.load_email(trade_id)
    return {"ok": True, "trade": trade, "email": email}


# ── 2. parse_our_confirmation ─────────────────────────────────────────

def parse_our_confirmation(trade_id: str) -> dict:
    raw_text = data.load_our_confirmation(trade_id)
    result = llm.parse_confirmation(raw_text)
    return {"ok": True, "parsed": result["data"], "tokens": result["tokens"], "raw_text": raw_text}


# ── 3. parse_counterparty_confirmation ────────────────────────────────

def parse_counterparty_confirmation(trade_id: str, version: str) -> dict:
    raw_text = data.load_cpty_confirmation(trade_id, version)
    if raw_text is None:
        return {"ok": False, "missing": True, "parsed": None, "tokens": {"input": 0, "output": 0}}
    result = llm.parse_confirmation(raw_text)
    return {"ok": True, "parsed": result["data"], "tokens": result["tokens"], "raw_text": raw_text}


# ── 4. get_custodian_status ───────────────────────────────────────────

def get_custodian_status(trade_id: str) -> dict:
    status = data.load_custodian_status(trade_id)
    return {"ok": True, "custodian": status}


# ── 5. lookup_ssi_registry ───────────────────────────────────────────

def lookup_ssi_registry(counterparty: str, currency: str, settle_date: str, version: str) -> dict:
    """Look up the latest SSI for a counterparty+currency pair.
    v1 reads the stale snapshot. v2 reads the current registry with version history."""
    registry = data.load_ssi_registry(version)
    matches = []
    for entry in registry.get("parties", []):
        if entry["party"] == counterparty and entry["currency"] == currency:
            history = entry.get("history", [])
            if version == "v1":
                # v1 just takes the last entry (only version 1 exists in snapshot)
                if history:
                    matches.append({"purpose": entry.get("purpose"), **history[-1]})
            else:
                # v2 takes the latest version effective on or before settle_date
                valid = [h for h in history if h.get("effective_from", "") <= settle_date]
                if valid:
                    latest = max(valid, key=lambda h: h.get("effective_from", ""))
                    matches.append({"purpose": entry.get("purpose"), **latest})
    return {"ok": bool(matches), "instructions": matches}


# ── 6. resolve_bank_branch ───────────────────────────────────────────

def resolve_bank_branch(bank_code: str) -> dict:
    directory = data.load_bank_directory()
    if bank_code in directory:
        return {"ok": True, "resolved": directory[bank_code]}
    return {"ok": False, "resolved": None, "error": f"Unknown bank code: {bank_code}"}


# ── 7. check_entity_account ──────────────────────────────────────────

def check_entity_account(
    account_on_confirm: str,
    bank_code_on_confirm: str,
    registry_instructions: list[dict],
    purpose_hint: str | None = None,
) -> dict:
    """Check whether the account on a confirmation matches the correct registry entry.
    When there are multiple accounts under the same bank code, use purpose_hint."""
    breaks = []
    if not registry_instructions:
        breaks.append({"field": "ssi_registry", "issue": "No registry entry found"})
        return {"ok": False, "breaks": breaks}

    # Find the right instruction by purpose or match
    best = None
    for instr in registry_instructions:
        if purpose_hint and instr.get("purpose") == purpose_hint:
            best = instr
            break
    if best is None:
        # Fall back to matching by account number
        for instr in registry_instructions:
            if instr.get("account") == account_on_confirm:
                best = instr
                break
    if best is None:
        # Just take the first one if there's only one
        if len(registry_instructions) == 1:
            best = registry_instructions[0]
        else:
            breaks.append({
                "field": "account",
                "issue": "Multiple accounts available, cannot determine correct one",
                "accounts": [i.get("account") for i in registry_instructions],
                "confirm_account": account_on_confirm,
            })
            return {"ok": False, "breaks": breaks}

    # Check account
    if _norm(account_on_confirm) != _norm(best.get("account", "")):
        breaks.append({
            "field": "account",
            "our_value": account_on_confirm,
            "registry_value": best.get("account"),
            "issue": "Account mismatch with registry",
        })

    # Check bank code
    if _norm(bank_code_on_confirm) != _norm(best.get("bank_code", "")):
        breaks.append({
            "field": "bank_code",
            "our_value": bank_code_on_confirm,
            "registry_value": best.get("bank_code"),
            "issue": "Bank code mismatch with registry",
        })

    return {"ok": len(breaks) == 0, "breaks": breaks, "matched_instruction": best}


# ── 8. cross_match_sides ─────────────────────────────────────────────

def cross_match_sides(our_parsed: dict, cpty_parsed: dict) -> dict:
    """Check that both parties agree on where money goes.

    Counterparty confirmations may describe things from EITHER perspective:
    - "Pay cash to X" means the counterparty wants us to send to X (= our pay = their receive)
    - They may or may not include a receive section

    Strategy: collect all account/bank pairs from each side, then check that
    our pay target appears somewhere in the counterparty's instructions, and
    our receive target appears somewhere too (if the counterparty mentions it).
    """
    breaks = []

    our_pay_acct = _norm(our_parsed.get("pay_account") or "")
    our_pay_code = _norm(our_parsed.get("pay_bank_code") or "")
    our_recv_acct = _norm(our_parsed.get("receive_account") or "")
    our_recv_code = _norm(our_parsed.get("receive_bank_code") or "")

    # Collect all accounts mentioned by the counterparty
    cpty_accounts = set()
    cpty_codes = set()
    for prefix in ("pay", "receive"):
        a = _norm(cpty_parsed.get(f"{prefix}_account") or "")
        c = _norm(cpty_parsed.get(f"{prefix}_bank_code") or "")
        if a:
            cpty_accounts.add(a)
        if c:
            cpty_codes.add(c)

    # Our pay account should be mentioned by the counterparty
    if our_pay_acct and cpty_accounts:
        if our_pay_acct not in cpty_accounts:
            breaks.append({
                "field": "pay_account",
                "issue": "Our pay account not found in counterparty confirmation",
                "our_pay": our_parsed.get("pay_account"),
                "cpty_accounts": sorted(cpty_accounts),
            })

    if our_pay_code and cpty_codes:
        if our_pay_code not in cpty_codes:
            breaks.append({
                "field": "pay_bank_code",
                "issue": "Our pay bank code not found in counterparty confirmation",
                "our_pay_bank": our_parsed.get("pay_bank_code"),
                "cpty_bank_codes": sorted(cpty_codes),
            })

    # Swapped-sides detection: if counterparty has BOTH pay and receive fields,
    # check for the classic swap where they copied our perspective.
    # In a correct confirmation, cpty "Pay to" = counterparty's account (where we send).
    # In a swapped one, cpty "Pay to" = OUR account (they're telling us to pay ourselves).
    cpty_pay_acct = _norm(cpty_parsed.get("pay_account") or "")
    cpty_recv_acct = _norm(cpty_parsed.get("receive_account") or "")
    if cpty_pay_acct and cpty_recv_acct:
        # If cpty "Pay to" matches our receive AND cpty "Receive at" matches our pay,
        # they've written the confirmation from our perspective = swapped sides
        if (our_recv_acct and cpty_pay_acct == our_recv_acct and
                our_pay_acct and cpty_recv_acct == our_pay_acct):
            breaks.append({
                "field": "swapped_sides",
                "issue": "Counterparty confirmation has pay and receive swapped — "
                         "their 'Pay to' is our receive account and their 'Receive at' is our pay account",
                "our_pay": our_parsed.get("pay_account"),
                "our_receive": our_parsed.get("receive_account"),
                "cpty_pay": cpty_parsed.get("pay_account"),
                "cpty_receive": cpty_parsed.get("receive_account"),
            })

    return {"ok": len(breaks) == 0, "breaks": breaks}


# ── 9. compare_economics ─────────────────────────────────────────────

def compare_economics(trade: dict, our_parsed: dict, cpty_parsed: dict | None) -> dict:
    """Compare amounts, rate/price, and dates across trade and counterparty confirmation.

    The counterparty may describe amounts from either perspective (ours or theirs),
    so we compare the SET of amounts rather than matching buy/sell labels.
    """
    breaks = []
    if cpty_parsed is None:
        return {"ok": True, "breaks": [], "note": "No counterparty confirmation to compare"}

    # Collect the two amounts from each source as a set
    trade_amounts = set()
    cpty_amounts = set()
    for field in ["amount_bought", "amount_sold"]:
        tv = _to_num(trade.get(field))
        cv = _to_num(cpty_parsed.get(field))
        if tv is not None:
            trade_amounts.add(tv)
        if cv is not None:
            cpty_amounts.add(cv)

    # Both sides should mention the same set of amounts
    if trade_amounts and cpty_amounts and trade_amounts != cpty_amounts:
        # Check if there's a real mismatch (not just perspective flip)
        unmatched_trade = trade_amounts - cpty_amounts
        unmatched_cpty = cpty_amounts - trade_amounts
        # Allow tolerance of 1 unit
        real_mismatch = True
        if len(unmatched_trade) == len(unmatched_cpty):
            paired = list(zip(sorted(unmatched_trade), sorted(unmatched_cpty)))
            real_mismatch = any(abs(a - b) > 1 for a, b in paired)
        if real_mismatch:
            breaks.append({
                "field": "amounts",
                "trade_amounts": sorted(trade_amounts),
                "cpty_amounts": sorted(cpty_amounts),
                "issue": "Amount mismatch between trade and counterparty",
            })

    # Compare rate/price
    tr = _to_num(trade.get("rate_or_price"))
    cr = _to_num(cpty_parsed.get("rate_or_price"))
    if tr is not None and cr is not None and abs(tr - cr) > 0.0001:
        breaks.append({
            "field": "rate_or_price",
            "trade_value": tr,
            "cpty_value": cr,
            "issue": "Rate/price mismatch",
        })

    # Compare currencies as a set (don't care about buy/sell direction)
    trade_ccys = set()
    cpty_ccys = set()
    for field in ["ccy_bought", "ccy_sold"]:
        tv = (trade.get(field) or "").upper()
        cv = (str(cpty_parsed.get(field) or "")).upper()
        if tv:
            trade_ccys.add(tv)
        if cv:
            cpty_ccys.add(cv)
    if trade_ccys and cpty_ccys and trade_ccys != cpty_ccys:
        breaks.append({
            "field": "currencies",
            "trade_ccys": sorted(trade_ccys),
            "cpty_ccys": sorted(cpty_ccys),
            "issue": "Currency mismatch",
        })

    # Compare dates
    td = _norm_date(trade.get("settle_date") or "")
    cd = _norm_date(cpty_parsed.get("settle_date") or "")
    if td and cd and td != cd:
        breaks.append({"field": "settle_date", "trade_value": td, "cpty_value": cd, "issue": "Settlement date mismatch"})

    return {"ok": len(breaks) == 0, "breaks": breaks}


# ── 10. estimate_fail_cost ───────────────────────────────────────────

def estimate_fail_cost(trade: dict, demo_date: str) -> dict:
    """Flat 5000 + 5% annual on cash amount per day past value date."""
    amount = _to_num(trade.get("amount_sold")) or _to_num(trade.get("amount_bought")) or 0
    ccy = trade.get("ccy_sold") or trade.get("ccy_bought") or "USD"
    settle = trade.get("settle_date", "")
    if settle <= demo_date:
        days_late = 1
    else:
        days_late = 0
    flat = 5000
    interest = amount * 0.05 / 365 * max(days_late, 1)
    total = flat + interest
    return {
        "ok": True,
        "estimated_penalty": round(total, 2),
        "currency": ccy,
        "days_late": days_late,
        "note": "Demo estimate only. Flat 5000 + 5% annual per day.",
    }


# ── 11. decide ───────────────────────────────────────────────────────

def decide(all_breaks: list[dict], missing_cpty: bool, fault: str = "none", urgency: str = "none") -> dict:
    """Release only when every check is clean. Otherwise Hold."""
    if missing_cpty:
        return {"decision": "Hold", "reason": "Missing counterparty confirmation — chase required",
                "fault": fault, "urgency": urgency}
    if all_breaks:
        return {"decision": "Hold", "reason": f"{len(all_breaks)} break(s) found — fault {fault}, {urgency}",
                "fault": fault, "urgency": urgency}
    return {"decision": "Release", "reason": "All checks passed", "fault": "none", "urgency": "none"}


def assign_fault(
    our_parsed: dict,
    cpty_parsed: dict | None,
    registry_instructions: list[dict],
    all_breaks: list[dict],
    missing_cpty: bool,
    purpose: str | None = None,
) -> str:
    """Whose confirmation disagrees with the registry. Both wrong means our
    registry copy was never updated, which is ours to fix."""
    if missing_cpty:
        return "counterparty"
    if not all_breaks:
        return "none"
    if any(b.get("field") == "swapped_sides" for b in all_breaks):
        return "counterparty"

    expected = _expected_instruction(registry_instructions, purpose)
    if expected is None:
        return "unknown"

    def matches(acct: str, code: str) -> bool | None:
        if not acct and not code:
            return None
        return (_norm(acct) == _norm(expected.get("account", ""))
                and _norm(code) == _norm(expected.get("bank_code", "")))

    ours = matches(our_parsed.get("pay_account") or "", our_parsed.get("pay_bank_code") or "")
    theirs = None
    if cpty_parsed:
        theirs = matches(cpty_parsed.get("pay_account") or "", cpty_parsed.get("pay_bank_code") or "")

    if ours is False:
        return "us"
    if theirs is False:
        return "counterparty"
    return "unknown"


def _expected_instruction(registry_instructions: list[dict], purpose: str | None) -> dict | None:
    if purpose:
        for instr in registry_instructions:
            if instr.get("purpose") == purpose:
                return instr
    if len(registry_instructions) == 1:
        return registry_instructions[0]
    return None


def urgency_for(settle_date: str, demo_date: str, has_issue: bool) -> str:
    """Call when the trade settles today or earlier; email otherwise."""
    if not has_issue:
        return "none"
    return "call" if settle_date <= demo_date else "email"


# ── 12. draft_message ────────────────────────────────────────────────
# This is in llm.py since it requires model calls.


# ── Helpers ──────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    """Normalize for comparison: strip, uppercase, remove dashes."""
    return s.strip().upper().replace("-", "").replace(" ", "")


def _norm_date(s: str) -> str:
    """Normalize date to YYYY-MM-DD."""
    s = s.strip()
    if not s:
        return ""
    # Handle DD/MM/YYYY
    parts = s.split("/")
    if len(parts) == 3 and len(parts[2]) == 4:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    # Handle DD.MM.YYYY
    parts = s.split(".")
    if len(parts) == 3 and len(parts[2]) == 4:
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return s


def _to_num(val) -> float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None
