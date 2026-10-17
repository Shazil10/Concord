# Concord — pre-settlement verification agent

**Track:** Money Operations · MONEY TALKS 2 (Block Convey) · Oct 17, 2026

> Nothing gets paid until every party agrees.

Concord checks every trade against every party's version of it, and against the latest settlement instructions, before money moves. It says **Release** or **Hold**, says whether to call (settles today) or email, explains why, and drafts the follow-up message. A human reads a one-page summary and clicks approve.

Judging checklist lives in [MONEY_OPERATIONS.md](./MONEY_OPERATIONS.md). Who does what lives in [TASK_SPLIT.md](./TASK_SPLIT.md).

---

## 1. The problem

Before a trade settles, the same trade exists in several places:

- the **front office** booking (e.g. Bloomberg)
- **our** treasury system and the confirmation it generates
- the **counterparty's** confirmation
- the **custodian** who actually moves the cash or securities
- the **standing settlement instructions (SSIs)** of each side: which bank, which branch, which account

Back-office analysts compare all of these field by field, by hand, before they release payment. When something slips, the trade fails. Whoever caused the fail pays a penalty plus interest, and the client's portfolio is not filled.

Every bank's back office has this problem. It is the same across FX, bonds, and money markets: check trade economics, check both sides' instructions, check where it settles.

### The four failures that actually hurt

| Failure | What goes wrong |
|---|---|
| **Wrong beneficiary, same bank** | Right bank, wrong branch or country (e.g. Citi Korea instead of Citi New York). |
| **Stale instructions** | The counterparty changed its SSIs; we paid using the old ones. |
| **One bank code, several accounts** | The bank code identifies the institution, but the account line decides which fund gets the money. Pass on the code alone and the money lands in the wrong fund. |
| **Swapped sides** | Our receive account is compared to their receive account instead of their pay account. Both numbers look "right"; the money still goes to the wrong place. |

### Why now

Shared SSI databases already exist, and the industry is buying confirmation-matching software. Failures still happen because instructions are not checked against the **latest version at the moment of release**. The gap is verification, not storage. That is what an agent does.

---

## 2. What we are building

**Concord** — an agent that runs one trade through a fixed verification pipeline and hands a human a decision.

### In scope

- Any product with the same shape: **FX** and **bonds** in the demo, to prove it is generic.
- One generic trade model. No product-specific special cases.
- A mock **SSI registry** with versions and effective dates, standing in for a shared, real-time instruction layer.
- Release or Hold, with reasons, fault assignment (us or counterparty), call or email urgency, and a drafted message.
- A human approval queue.

### Out of scope

- Real SWIFT, real custodians, real Bloomberg, real payments. **Approve puts the message in a simulated outbox. Nothing is sent.**
- Blockchain / tokenization. It is the closing vision slide, not the build.
- Real or internal data. **Synthetic data only.** Internal procedure documents stay off GitHub, off PRISM, and out of model prompts.

### Who does what inside Concord

| Layer | Responsibility |
|---|---|
| **Plain code (tools)** | Every comparison: amounts, dates, rates, bank codes, accounts, side mapping. Deterministic and testable. |
| **Model (via Nicrron)** | Read messy confirmations and emails, explain each break in plain English, draft the message. Fault and call-vs-email are decided in code. |
| **Human** | Read the one-page summary, Approve or Hold. |
| **PRISM** | Record every run, cluster failures, fire alerts, prove the fix. |

Agents can misread an account too. That is why comparisons are code, the model explains, PRISM watches every run, and a human signs off.

---

## 3. How a run works

One run = one trade.

```
load_trade
  → parse_our_confirmation
  → parse_counterparty_confirmation
  → get_custodian_status
  → lookup_ssi_registry          (latest version + effective date)
  → resolve_bank_branch          (bank code → institution, branch, country)
  → check_entity_account         (right fund/account, not just right bank)
  → cross_match_sides            (our pay ↔ their receive, our receive ↔ their pay)
  → compare_economics            (amounts, rate/price, currency, dates)
  → estimate_fail_cost           (penalty + interest if it fails)
  → decide                       (Release / Hold + fault + call or email)
  → draft_message                (email or amend request)
  → human approval               (Ninoo UI → simulated outbox)
```

That is 12 tool steps, well over the 6 required for the PRISM Sessions proof.

### Output per trade

- **Decision:** Release / Hold, with urgency call (settles today) or email
- **Breaks:** each field that failed, with the value from each source
- **Fault:** us / counterparty / custodian / unknown
- **Urgency:** settles today? penalty exposure?
- **Draft message:** to the trader, counterparty, or custodian
- **Summary:** one page a human can approve in 30 seconds

---

## 4. Nicrron × Ninoo

| Tool | Use |
|---|---|
| **Nicrron API** | All model calls. `base_url=https://api.nicrron.ai/v1`, key in `.env` as `NICRRON_API_KEY`. Start with `nicrron/auto`; pin a model once prompts are stable. |
| **Nicrron Playground** | Test parsing and explanation prompts on sample confirmations before wiring them. |
| **Ninoo Builder** | Demo UI: trade queue → open trade → summary + breaks → Approve / Hold → outbox. Published at `*.ninoo.app`. |
| **Ninoo Code** | Optional. Cursor is fine. |

Credits ($260 each) expire **Oct 18, 6:00 PM ET**.

---

## 5. PRISM — the three proofs

### Sessions (6+ steps)

Open one trade run on the **Steps** tab. Every tool in §3 appears as its own step.

### Root Cause — stale instructions

- **v1 bug:** `lookup_ssi_registry` reads a cached snapshot instead of the latest version. Every trade where the counterparty changed its SSIs gets wrongly marked **Release**.
- Run all scenarios. Tick 5–10 failing runs → **Analyse selected** → Root Cause → **Analyze now**.
- Show the cluster (3+ runs) and its cause.
- **v2 fix:** look up the latest version and check its effective date against the settlement date. Same trades → **Hold**.
- Our one-sentence why: *the agent trusted saved instructions without checking whether they were still current, which is exactly how stale-SSI payments happen in real back offices.*
- Second fix if time allows: one bank code, several accounts.

### Alert — error rate

- **v1 bug:** a missing counterparty confirmation crashes `parse_counterparty_confirmation`, so the run ends with no decision. That counts toward error rate.
- Set an error-rate alert. Run the missing-confirmation scenarios. Show it firing.
- **v2:** a missing confirmation becomes a clean **Hold — chase counterparty** decision.
- Demo line: *this is the alert that would have caught it.*

### Volume

Get **50+ runs** into PRISM before fixing anything. ~20 trades × v1 × a few repeats gets us there. 200 runs/day are analysed per workspace.

---

## 6. Data

All synthetic. Vlad generates it; spec in [TASK_SPLIT.md](./TASK_SPLIT.md).

```
data/
  trades.csv                     front-office bookings
  our_confirmations/<id>.txt     our confirmation per trade
  cpty_confirmations/<id>.txt    counterparty confirmation (may be missing)
  custodian_status.csv           custodian view per trade
  ssi_registry.json              SSIs with versions + effective dates
  ssi_snapshot.json              stale cached copy (v1 reads this)
  bank_directory.csv             bank code → institution, branch, country
  emails/<id>.txt                counterparty emails (e.g. "we changed our account")
  scenarios.csv                  trade_id, product, failure_type, expected_decision
```

`scenarios.csv` is the answer key. It lets us score v1 vs v2 on the same inputs.

### Target mix (~20 trades)

| Scenario | Count | Expected |
|---|---|---|
| Clean match | 6 | Release |
| Stale instructions | 4 | Hold |
| Wrong branch, same bank | 3 | Hold |
| One bank code, several accounts | 3 | Hold |
| Swapped sides | 2 | Hold |
| Missing counterparty confirmation | 2 | Hold (chase) |

Mix FX and bonds across all rows.

---

## 7. Repo layout

```
concord/
  agent.py          pipeline + decision
  tools.py          deterministic checks
  llm.py            Nicrron client + prompts
  tracing.py        PRISM setup
  run_batch.py      run all scenarios, print v1/v2 scorecard
data/               synthetic data (Vlad)
IDEA.md
TASK_SPLIT.md
MONEY_OPERATIONS.md
```

Versioned by a flag (`--version v1` / `--version v2`) so both run on the same inputs.

---

## 8. Demo (3 minutes)

1. **The problem (20s):** analysts check every trade by hand across five sources; one stale account number sends money to the wrong place.
2. **Concord UI (40s):** queue of trades → open a held trade → breaks, fault, draft email → Approve → outbox.
3. **PRISM Sessions (20s):** that run, 12 steps.
4. **The failure (30s):** Root Cause cluster — v1 released trades on stale instructions.
5. **The fix (30s):** v2 on the same inputs → all held. Scorecard v1 vs v2.
6. **The alert (20s):** error-rate alert firing on missing confirmations.
7. **Vision (20s):** every party on one shared, permissioned instruction layer; Concord is the verification agent on top.

---

## 9. Pitch line

*We work in World Bank Group Treasury, in trade operations and financial technology. Every day trades are checked field by field across five systems before money moves. Concord does that check, explains every break, and leaves the human one decision: approve.*

---

## 10. Rules

- Synthetic data only. No real accounts, cards, logins, or personal data.
- No internal documents in the repo, in PRISM, or in prompts.
- Keys in `.env` only.
- Concord never sends real messages or payments.
- AI output is a starting point, not financial advice.
