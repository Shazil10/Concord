# Task split — Concord

What we're building: [IDEA.md](./IDEA.md). Judging checklist: [MONEY_OPERATIONS.md](./MONEY_OPERATIONS.md).

Vlad works on the `vlad` branch, Shazil on `shazil`. PRs into `main`; Shazil merges.

---

## Vlad — data, realism, UI, pitch

### Synthetic data (first priority — Shazil is blocked on this)

- Put everything in `data/`, using the layout in IDEA.md §6.
- ~20 trades, FX and bonds mixed, following the scenario mix in IDEA.md §6.
- **Synthetic only.** Fake bank codes, fake accounts, fake names. Nothing copied from internal systems or procedure documents.
- `trades.csv` — front-office bookings. Suggested columns:
  - `trade_id, product, trade_date, settle_date, our_entity, counterparty, side, ccy_bought, amount_bought, ccy_sold, amount_sold, rate_or_price, security_id, quantity, settlement_location`
- `our_confirmations/<trade_id>.txt` — our confirmation, in a realistic SWIFT-like text format.
- `cpty_confirmations/<trade_id>.txt` — the counterparty's version. Leave the file out for "missing confirmation" scenarios.
  - Make some of them messy on purpose (different field order, extra notes, date formats) so the model has real parsing work.
- `custodian_status.csv` — `trade_id, custodian, status, expected_amount, expected_ccy, value_date, notes`.
- `ssi_registry.json` — current SSIs, **with version history**:
  - per party + currency: `bank_code, bank_name, branch_country, account, version, effective_from`
  - for stale-SSI scenarios, include a newer version whose `effective_from` is before the settle date.
- `ssi_snapshot.json` — the old cached copy (missing those newer versions). v1 reads this.
- `bank_directory.csv` — `bank_code, institution, branch, country`. Include same-bank-different-branch pairs (e.g. one bank in New York and in Seoul).
- `emails/<trade_id>.txt` — counterparty emails where they matter (e.g. "please note our new USD account effective …").
- `scenarios.csv` — the answer key:
  - `trade_id, product, failure_type, expected_decision, expected_fault, notes`
  - `failure_type` is one of: `clean, stale_ssi, wrong_branch, shared_code_wrong_account, swapped_sides, missing_cpty_confirm`

### Realism check

- Write the real-world reconciliation steps in plain English (generic, no internal names), so we can confirm the agent's pipeline matches how a back office actually works.
- Review the agent's break explanations and draft emails. Do they sound like what an ops analyst would send?
- Tell us when to email vs escalate urgently (settles today, penalty size).

### Demo UI (Ninoo Builder)

- Build in Ninoo Builder at `app.ninoo.ai`:
  - **Queue:** all trades with status Release / Hold.
  - **Trade view:** one-page summary, table of breaks (field, our value, their value, registry value), fault, urgency.
  - **Draft message** panel.
  - **Approve / Hold** buttons → **Outbox** list (simulated, nothing sent).
- Shazil will give you a JSON output file per trade to wire in.
- Publish and share the `*.ninoo.app` link.

### Pitch

- Own the 20-second problem story: what happens in real life when one stale account number gets paid.
- Closing vision slide: a shared, permissioned instruction layer across all parties, with Concord as the verification agent on top.
- Rehearse the 3-minute demo with Shazil (IDEA.md §8).

---

## Shazil — agent, Nicrron, PRISM, integration

### Setup

- Python project skeleton in `concord/` (IDEA.md §7).
- Load `PRISM_API_KEY` and `NICRRON_API_KEY` from `.env`.
- Wire `prismtrace-sdk`. Confirm a dummy 6-step run shows on PRISM's Steps tab **before** building real logic.
- Until Vlad's data lands, use 2–3 stub trades so the pipeline can run.

### Agent

- Tools in `tools.py`, each traced as its own step:
  - `load_trade`, `parse_our_confirmation`, `parse_counterparty_confirmation`, `get_custodian_status`, `lookup_ssi_registry`, `resolve_bank_branch`, `check_entity_account`, `cross_match_sides`, `compare_economics`, `estimate_fail_cost`, `decide`, `draft_message`.
- All comparisons in plain code.
- Model calls (via Nicrron) only for: parsing messy confirmations and emails, explaining breaks, assigning fault, choosing urgency, drafting messages.
- Test prompts in the Nicrron Playground first.
- Output one JSON per trade for the UI: decision, breaks, fault, urgency, draft message, summary.

### v1 / v2

- `--version v1 | v2` flag, same inputs.
- **v1 bugs (on purpose, realistic):**
  - reads `ssi_snapshot.json` instead of the latest registry version (stale SSIs → wrongly Release)
  - crashes on a missing counterparty confirmation (no decision → error rate)
- **v2 fixes:**
  - latest registry version + effective date check against settle date
  - missing confirmation → clean "Hold — chase counterparty"
- Stretch: one-bank-code-several-accounts check as a second fix.
- `run_batch.py`: run all scenarios, compare to `scenarios.csv`, print a v1 vs v2 scorecard.

### PRISM proofs

- Get **50+ runs** in before fixing anything.
- **Sessions:** pick one clean run with all 12 steps; screenshot.
- **Root Cause:** tick 5–10 failing v1 runs → Analyse selected → Root Cause → Analyze now. Cluster of 3+ with cause. Then v2 on the same inputs passing.
- **Alert:** error-rate alert; show it firing on v1 missing-confirmation runs.
- Save screenshots of all three for the submission.

### Integration and submission

- Hand Vlad the per-trade JSON for the Ninoo UI.
- Keep `IDEA.md` and `MONEY_OPERATIONS.md` checklist current.
- Review and merge PRs into `main`.
- Final repo clean: no `.env`, no internal docs, README with how to run.
- Submission write-up and links (repo, Ninoo app, PRISM screenshots).

---

## Timeline (today)

| Time | Vlad | Shazil |
|---|---|---|
| 11:45–1:00 | Synthetic data + scenarios.csv | Skeleton, PRISM + Nicrron wired, stub run on Steps tab |
| 1:00–2:30 | Ninoo UI first version; realism review | Full v1 agent on real data; 50+ runs into PRISM |
| 2:30–3:30 | Wire UI to agent output | Root Cause analysis, alert, v2 fixes, scorecard |
| 3:30–4:30 | Pitch story + vision slide | v2 runs, PRISM screenshots, README |
| 4:30–end | Rehearse demo together; submit | |
