"""PRISM tracing helpers. Each tool step is sent as part of a trajectory."""

from __future__ import annotations

import time
from typing import Any, Callable

from prismtrace import PRISMtrace

from concord.config import PRISMTRACE_API_KEY, PRISMTRACE_HOST, PRISMTRACE_PROJECT_ID

_pt: PRISMtrace | None = None


def get_client() -> PRISMtrace:
    global _pt
    if _pt is None:
        _pt = PRISMtrace(
            api_key=PRISMTRACE_API_KEY,
            host=PRISMTRACE_HOST,
            project_id=PRISMTRACE_PROJECT_ID,
        )
    return _pt


def step(name: str, input_summary: str, fn: Callable[[], Any], is_llm: bool = False) -> dict:
    """Run a tool function, time it, and return a trajectory step dict.

    On error, the step is marked status=error and the exception is re-raised.
    """
    t0 = time.perf_counter()
    try:
        result = fn()
        elapsed = int((time.perf_counter() - t0) * 1000)
        output_summary = _summarize(result)
        tokens = 0
        if isinstance(result, dict) and "tokens" in result:
            t = result["tokens"]
            tokens = (t.get("input", 0) or 0) + (t.get("output", 0) or 0)
        s = {
            "step_type": "tool_call",
            "label": name,
            "tool_name": name,
            "input_summary": input_summary[:500],
            "output_summary": output_summary[:500],
            "duration_ms": elapsed,
            "status": "success",
        }
        if tokens:
            s["token_count"] = tokens
        return {"step": s, "result": result}
    except Exception as exc:
        elapsed = int((time.perf_counter() - t0) * 1000)
        s = {
            "step_type": "tool_call",
            "label": name,
            "tool_name": name,
            "input_summary": input_summary[:500],
            "output_summary": f"ERROR: {type(exc).__name__}: {exc}"[:500],
            "duration_ms": elapsed,
            "status": "error",
        }
        return {"step": s, "result": None, "error": exc}


def _summarize(result: Any) -> str:
    if not isinstance(result, dict):
        return str(result)[:200]
    if result.get("decision"):
        return f"{result['decision']}: {result.get('reason', '')}"
    if "parsed" in result:
        p = result["parsed"]
        if not p:
            return "no counterparty confirmation on file"
        return (f"parsed {p.get('trade_id', '?')}: pay {p.get('pay_bank_code') or '-'} "
                f"{p.get('pay_account') or '-'}, receive {p.get('receive_bank_code') or '-'} "
                f"{p.get('receive_account') or '-'}")
    if "trade" in result:
        t = result["trade"]
        return (f"{t.get('product')} {t.get('counterparty')} settles {t.get('settle_date')}"
                f"{', email on file' if result.get('email') else ''}")
    if "custodian" in result:
        c = result["custodian"] or {}
        return ", ".join(f"{k}={v}" for k, v in c.items() if k != "trade_id")[:200]
    if "instructions" in result:
        ins = result["instructions"]
        if not ins:
            return "no registry entry"
        return "; ".join(f"{i.get('purpose')}: {i.get('bank_code')} {i.get('account')} "
                         f"(v{i.get('version')} from {i.get('effective_from')})" for i in ins)
    if "resolved" in result:
        r = result["resolved"]
        return f"{r.get('institution', '')} {r.get('branch', '')}, {r.get('country', '')}" if r else result.get("error", "unknown")
    if "estimated_penalty" in result:
        return f"est. fail cost {result['estimated_penalty']:,.0f} {result.get('currency', '')}"
    if "data" in result and isinstance(result["data"], dict) and "message" in result["data"]:
        return f"to {result['data'].get('recipient', '?')}: {result['data']['message']}"
    if "ok" in result:
        breaks = result.get("breaks", [])
        if breaks:
            return f"{len(breaks)} break(s): " + "; ".join(
                f"{b.get('field', '?')} — {b.get('issue', '')}" for b in breaks[:3])
        return result.get("note") or "match"
    return str(result)[:200]
