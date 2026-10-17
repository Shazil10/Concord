# Money Operations — do not forget this

We are on **Money Operations**. Tracks are themes, not assignments. Whatever we ship, these two things are required or we do not place:

1. **PRISM** — show all three Operations proofs below.
2. **NicrronNinoo** — every model call goes through the Nicrron API (or the app is built/published through Ninoo).

Judges score **Build → Observe → Improve → Demo**. A pretty UI without PRISM proofs is not enough.

---

## Platforms (required)

### Nicrron (brain)

- Base URL: `https://api.nicrron.ai/v1`
- Keys live in local `.env` only. Never commit `.env`.
- Use `nicrron/auto` or a named model (`anthropic/claude-sonnet-5`, `openai/gpt-5.5`, …).
- **Ninoo Builder** (`app.ninoo.ai`) is how we ship the demo UI the judges click.
- Ninoo Code is optional. Cursor is fine for writing the agent.

### PRISM (flight recorder)

- Workspace: one per team. Code already redeemed: `MONEYTALKS#2`.
- Instrument with `prismtrace-sdk` (or OpenTelemetry exporter).
- Nicrron key is the model key.
- Tracing/analysis are free. **200 runs/day analysed per workspace.**
- Get **50+ runs** into PRISM before we spend the afternoon polishing.

---

## The three PRISM proofs (all required)

### 1. Sessions — 6+ tool-call steps

- Open **one run → Steps tab**.
- Show **every tool call** the agent makes.
- Need **6 or more steps** on that run.
- Design the agent with real tools (list files, read source, query ledger, match, flag exception, draft brief). Do not hide work inside one giant LLM call.

### 2. Alert — must fire on a real run

- Set an alert on something that matters to the workflow:
  - latency
  - error rate
  - satisfaction score
- **A failed tool call that leaves the run with no answer counts toward error rate.**
- Screenshot / live-show the alert **firing on a real run**, not a mock.

### 3. Root Cause — cluster, then v2 that no longer fails

Exact sequence:

1. Get failing runs into PRISM (same bug repeated is good).
2. **Traces → tick 5 to 10 failing runs → Analyse selected** (1 credit each).
3. **Root Cause page → Analyze now** (5 credits).
4. Show a **cluster of 3+ failed runs** and its cause.
5. Ship **v2** and re-run the **same inputs**. Those runs must **no longer fail**.

---

## Demo script (this is the pitch)

**The failure, the fix, and the alert that would have caught it.**

Suggested 3-minute flow:

1. **Ninoo Builder UI** — product: upload / run / CFO-style brief or exception list.
2. **PRISM Sessions** — one rich run with 6+ tool steps.
3. **PRISM Root Cause** — v1 cluster of 3+ failures + one-sentence “why.”
4. **Same inputs on v2** — no longer failing.
5. **PRISM Alert** — the alert that fired (or would have caught) that failure.

Do **not** demo “UI before PRISM vs UI after PRISM.”  
Demo **broken agent vs fixed agent**, both traced, plus the product UI.

---

## Day-of build order

1. Thin agent with **6+ explicit tools** + Nicrron + PRISM tracing.
2. Messy sample data (never real cards, logins, or anyone’s personal finance).
3. Flood PRISM with **50+ runs** (good, bad, missing files, bad IDs).
4. Analyse 5–10 failures → Root Cause cluster.
5. One sharp v2 fix. Re-run the same failing inputs.
6. Alert on error rate / failed tool / latency — confirm it fires.
7. Ninoo Builder UI for the live demo.
8. Practice the 3-minute script above.

Do not polish the UI until proofs 1–3 are in the bag.

---

## Safety

Use made-up or sample data only. AI output is a starting point, not financial advice.

---

## Quick checkbox (tick before we demo)

- [ ] Model calls go through Nicrron
- [ ] Demo UI is on Ninoo Builder (public link)
- [ ] One PRISM run shows 6+ tool steps
- [ ] Alert exists and has fired on a real run
- [ ] 5–10 failing runs analysed, then Root Cause → Analyze now
- [ ] Cluster of 3+ failed runs + cause
- [ ] v2 on the same inputs no longer fails
- [ ] Pitch: failure → fix → alert
