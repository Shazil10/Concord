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
    if isinstance(result, dict):
        ok = result.get("ok")
        decision = result.get("decision")
        breaks = result.get("breaks", [])
        if decision:
            return f"{decision}: {result.get('reason', '')}"
        if ok is not None:
            n = len(breaks)
            if n:
                return f"ok={ok}, {n} break(s): {', '.join(b.get('field','?') for b in breaks[:3])}"
            return f"ok={ok}"
        if "parsed" in result:
            p = result["parsed"]
            if p:
                return f"parsed: {p.get('trade_id', '?')} {p.get('counterparty', '?')}"
            return "parsed: None (missing)"
    return str(result)[:200]
