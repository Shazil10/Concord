# Concord — Pre-Settlement Trade Verification Agent

> **Money Talks 2 — AI × Finance Hackathon** | Money Operations track  
> Built by Shazil Farukh & Vladislav Pak (World Bank Group Treasury)

**Concord** checks every trade against every party's confirmation and the latest settlement instructions before money moves. It hands a human one decision: **Release** or **Hold**. Every Hold says whose fault it is and whether to **call** (settles today) or **email**.

**Demo video (1 min):** [Watch on Loom](https://www.loom.com/share/de3117b0a92b4babbe6bed9ad292f5ae)

**Demo site:** [empty-react-app-6c23.ninoo.app](https://empty-react-app-6c23.ninoo.app/), built on Ninoo Builder. The source is `ui/site/App.tsx`.

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/Shazil10/Concord.git
cd Concord
pip install openai python-dotenv prismtrace-sdk

# 2. Set up secrets (copy the example and fill in your keys)
cp .env.example .env
# Edit .env with your NICRRON_API_KEY and PRISM_API_KEY

# 3. Run v2 (the fixed agent) on all 20 trades
python -m concord.run_batch --version v2

# 4. Run v1 (the buggy agent) to see the before-picture
python -m concord.run_batch --version v1
```

## How it works

Concord runs a 12-step pipeline for each trade:

| Step | Tool | What it does |
|------|------|--------------|
| 1 | `load_trade` | Load trade + email from data files |
| 2 | `parse_our_confirmation` | LLM parses our SWIFT-style confirmation |
| 3 | `parse_counterparty_confirmation` | LLM parses the counterparty's confirmation |
| 4 | `get_custodian_status` | Check custodian readiness and cash cutoffs |
| 5 | `lookup_ssi_registry` | Look up latest SSI for the counterparty |
| 6 | `resolve_bank_branch` | Verify bank code → branch mapping |
| 7 | `check_entity_account` | Compare our pay account against the registry |
| 8 | `cross_match_sides` | Verify both sides agree on where money goes |
| 9 | `compare_economics` | Compare amounts, rate, dates across sources |
| 10 | `estimate_fail_cost` | Estimate penalty if settlement fails |
| 11 | `decide` | Release (clean) or Hold (breaks found) |
| 12 | `draft_message` | LLM drafts call/email for the operations desk |

## v1 vs v2

| Version | What's different | Score |
|---------|-----------------|-------|
| **v1** (buggy) | Reads stale SSI snapshot; crashes on missing counterparty confirmation | 14/20 (70%) |
| **v2** (fixed) | Reads current registry with version history; gracefully handles missing confirmations | 20/20 (100%) |

Fault (us or counterparty) is assigned in code, not by the model: whichever confirmation disagrees with the registry is at fault, and if both carry a stale instruction the fault is ours. Urgency is call when the trade settles today, email otherwise. v2 gets fault right on 20/20.

## Failure types detected

1. **Stale SSI** — Our confirmation uses an outdated account number. Registry has the update.
2. **Wrong branch** — Counterparty quotes a different branch/bank code than what's on record.
3. **Shared code, wrong account** — Same bank code, multiple accounts. We picked the wrong one.
4. **Swapped sides** — Counterparty copied our confirmation as theirs (pay ↔ receive swapped).
5. **Missing confirmation** — No counterparty confirmation received. Chase required.

## Project structure

```
concord/
  config.py       — Environment + constants
  data.py         — Load trades, confirmations, SSI, custodian status
  llm.py          — Nicrron (Fable) calls: parse, explain, draft
  tools.py        — The 12 pipeline tools
  tracing.py      — PRISM trajectory + step tracing
  agent.py        — run_trade(): orchestrates the 12-step pipeline
  run_batch.py    — CLI: batch run + scorecard vs scenarios.csv
data/
  scenarios.csv   — Answer key (20 trades, expected decisions)
  ssi_registry.json   — Current SSI (v2 reads this)
  ssi_snapshot.json   — Stale SSI (v1 reads this)
  our_confirmations/  — Our SWIFT-style confirmations
  cpty_confirmations/ — Counterparty confirmations
  emails/             — Settlement desk emails
results/
  v1.json         — v1 batch results
  v2.json         — v2 batch results (used by Ninoo UI)
ui/
  NINOO.md        — Ninoo Builder prompt
  sample_queue.json — Trade queue data for the UI
```

## PRISM proofs

- **Sessions**: Each trade run produces 12 tool steps visible on the PRISM Steps tab
- **Alert**: v1 crashes on T019/T020 (FileNotFoundError) trigger error-rate alerts
- **Root Cause**: 8+ crash sessions cluster around the same missing-confirmation bug; v2 fixes them all

## Tech stack

- **Model**: `anthropic/claude-fable-5-1` via [Nicrron API](https://api.nicrron.ai/v1)
- **Observability**: [PRISM by Block Convey](https://prism.blockconvey.com) via `prismtrace-sdk`
- **UI**: [Ninoo Builder](https://app.ninoo.ai) (describe → publish)
- **Data**: 20 synthetic trades, 10 counterparties, realistic SWIFT-format confirmations

## Docs

- [IDEA.md](./IDEA.md) — Full project description
- [TASK_SPLIT.md](./TASK_SPLIT.md) — Who does what
- [MONEY_OPERATIONS.md](./MONEY_OPERATIONS.md) — PRISM judging checklist
- [REALISM.md](./REALISM.md) — Settlement workflow realism notes
