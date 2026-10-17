"""Smoke test: send a 6-step trajectory + one real Fable call to PRISM.

Run:  python -m concord.smoke
"""

from __future__ import annotations

import time
import uuid

from openai import OpenAI
from prismtrace import PRISMtrace
import prismtrace

from concord.config import (
    CONCORD_MODEL,
    NICRRON_API_KEY,
    NICRRON_BASE_URL,
    PRISMTRACE_API_KEY,
    PRISMTRACE_HOST,
    PRISMTRACE_PROJECT_ID,
)


def main() -> None:
    pt = PRISMtrace(
        api_key=PRISMTRACE_API_KEY,
        host=PRISMTRACE_HOST,
        project_id=PRISMTRACE_PROJECT_ID,
    )
    client = OpenAI(base_url=NICRRON_BASE_URL, api_key=NICRRON_API_KEY)

    session_id = f"smoke-{uuid.uuid4().hex[:8]}"
    steps: list[dict] = []

    # Step 1: load_trade
    t0 = time.perf_counter()
    trade = {"trade_id": "SMOKE01", "product": "FX", "counterparty": "Test Bank"}
    steps.append({
        "step_type": "tool_call",
        "label": "load_trade",
        "tool_name": "load_trade",
        "input_summary": "trade_id=SMOKE01",
        "output_summary": f"FX trade with Test Bank loaded",
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "status": "success",
    })

    # Step 2: parse_our_confirmation (LLM call via Fable)
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=CONCORD_MODEL,
        temperature=0,
        max_tokens=200,
        messages=[
            {"role": "system", "content": "You are a trade confirmation parser. Return JSON with fields: counterparty, amount, currency, account."},
            {"role": "user", "content": "OUR CONFIRMATION\nTrade id: SMOKE01\nWe buy EUR 1,000,000\nWe sell USD 1,090,000\nRate 1.0900\nPay to account: 90010001"},
        ],
    )
    llm_output = resp.choices[0].message.content
    steps.append({
        "step_type": "tool_call",
        "label": "parse_our_confirmation",
        "tool_name": "parse_our_confirmation",
        "input_summary": "OUR CONFIRMATION for SMOKE01",
        "output_summary": llm_output[:200] if llm_output else "parsed",
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "token_count": (resp.usage.prompt_tokens + resp.usage.completion_tokens) if resp.usage else 0,
        "status": "success",
    })
    print(f"  Fable call OK: {CONCORD_MODEL}")

    # Steps 3-5: deterministic checks
    for i, name in enumerate(["lookup_ssi_registry", "resolve_bank_branch", "cross_match_sides"], 3):
        t0 = time.perf_counter()
        steps.append({
            "step_type": "tool_call",
            "label": name,
            "tool_name": name,
            "input_summary": f"step {i} input",
            "output_summary": f"step {i} OK, no breaks",
            "duration_ms": max(1, int((time.perf_counter() - t0) * 1000)),
            "status": "success",
        })

    # Step 6: decide
    t0 = time.perf_counter()
    steps.append({
        "step_type": "final_answer",
        "label": "decide",
        "output_summary": "Release — all checks passed",
        "duration_ms": max(1, int((time.perf_counter() - t0) * 1000)),
        "status": "success",
    })

    # Send trajectory
    with prismtrace.session(session_id):
        result = pt.submit_trajectory(
            steps=steps,
            agent_name="concord",
            agent_id="concord",
            model=CONCORD_MODEL,
            final_status="success",
        )

    if result:
        print(f"  Trajectory submitted: id={result.get('id', '?')}")
    else:
        print("  WARNING: trajectory submission returned None")

    # Also send a trace_llm so PRISM sees a live trace
    with prismtrace.session(session_id):
        pt.trace_llm(
            model=CONCORD_MODEL,
            agent_name="concord",
            agent_id="concord",
            input_messages=[{"role": "user", "content": "smoke test"}],
            output="Release — all checks passed",
            latency_ms=sum(s.get("duration_ms", 0) for s in steps),
            token_count_input=resp.usage.prompt_tokens if resp.usage else 0,
            token_count_output=resp.usage.completion_tokens if resp.usage else 0,
            metadata={"version": "smoke", "trade_id": "SMOKE01"},
        )

    pt.flush(timeout=5)
    pt.close()
    print(f"\nSmoke test complete. Session: {session_id}")
    print("Check PRISM dashboard for the trajectory and trace.")


if __name__ == "__main__":
    main()
