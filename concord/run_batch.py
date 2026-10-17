"""Run all 20 trades through the Concord pipeline and score against scenarios.csv.

Usage:
    python -m concord.run_batch --version v1
    python -m concord.run_batch --version v2
    python -m concord.run_batch --version v1 --repeat 3
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback

from concord.agent import run_trade
from concord.config import RESULTS_DIR
from concord.data import load_scenarios, load_trades
from concord.tracing import get_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Concord batch")
    parser.add_argument("--version", required=True, choices=["v1", "v2"])
    parser.add_argument("--repeat", type=int, default=1, help="How many times to run the full set")
    parser.add_argument("--trades", nargs="*", help="Specific trade IDs to run (default: all)")
    args = parser.parse_args()

    scenarios = {s["trade_id"]: s for s in load_scenarios()}
    all_trades = load_trades()
    trade_ids = args.trades or [t["trade_id"] for t in all_trades]

    results = []
    correct = 0
    wrong = 0
    crashed = 0
    total = 0

    for rep in range(args.repeat):
        if args.repeat > 1:
            print(f"\n── Repeat {rep + 1}/{args.repeat} ──")

        for tid in trade_ids:
            total += 1
            expected = scenarios.get(tid, {})
            expected_decision = expected.get("expected_decision", "?")
            expected_fault = expected.get("expected_fault", "?")

            try:
                result = run_trade(tid, args.version, emit=False)
                actual_decision = result["decision"]
                actual_fault = result.get("fault", "?")

                decision_match = actual_decision == expected_decision
                # Don't check fault for clean Release trades
                fault_match = (expected_fault == "none" and actual_decision == "Release") or \
                              actual_fault == expected_fault

                # A Release on a trade that should be Held is the v1 stale-SSI bug.
                # Tag it so PRISM can cluster those runs. The agent itself never
                # reads the answer key; only this scorecard does.
                emit = result.pop("_emit")
                if expected_decision == "Hold" and actual_decision == "Release":
                    emit("wrong_release", "error")
                elif decision_match:
                    emit("correct", "success")
                else:
                    emit("wrong_decision", "error")

                if decision_match:
                    correct += 1
                    mark = "✓"
                else:
                    wrong += 1
                    mark = "✗"

                print(f"  {mark} {tid} {result['product']:4s} | "
                      f"expected={expected_decision:7s} got={actual_decision:7s} | "
                      f"fault expected={expected_fault:12s} got={actual_fault:12s} | "
                      f"{result.get('reason', '')[:50]}")

                results.append(result)

            except Exception as exc:
                crashed += 1
                print(f"  💥 {tid} CRASHED: {type(exc).__name__}: {exc}")
                traceback.print_exc(file=sys.stderr)
                results.append({
                    "trade_id": tid,
                    "version": args.version,
                    "decision": "CRASH",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "breaks": [],
                    "fault": "error",
                })

    # Scorecard
    print(f"\n{'='*60}")
    print(f"Scorecard: {args.version}")
    print(f"  Correct: {correct}/{total}")
    print(f"  Wrong:   {wrong}/{total}")
    print(f"  Crashed: {crashed}/{total}")
    print(f"  Score:   {correct}/{total} ({100*correct/max(total,1):.0f}%)")
    print(f"{'='*60}")

    # One row per trade in the saved file, even when --repeat flooded PRISM.
    by_id: dict[str, dict] = {}
    for row in results:
        by_id[row["trade_id"]] = row
    saved = [by_id[tid] for tid in trade_ids if tid in by_id]
    saved_correct = sum(1 for row in saved if row.get("decision") == scenarios.get(row["trade_id"], {}).get("expected_decision"))
    saved_crashed = sum(1 for row in saved if row.get("decision") == "CRASH")
    saved_wrong = len(saved) - saved_correct - saved_crashed

    # Write results JSON
    out_path = RESULTS_DIR / f"{args.version}.json"
    with open(out_path, "w") as f:
        json.dump({
            "version": args.version,
            "scorecard": {
                "correct": saved_correct,
                "wrong": saved_wrong,
                "crashed": saved_crashed,
                "total": len(saved),
            },
            "trades": saved,
        }, f, indent=2, default=str)
    print(f"\nResults written to {out_path} ({len(saved)} trades)")

    # Flush PRISM
    pt = get_client()
    pt.flush(timeout=10)
    pt.close()


if __name__ == "__main__":
    main()
