# Sample data

Fictional desk: **Northline Treasury**. Twenty trades, valued on **2026-10-17**. No real institution, account, or client is in this folder.

Regenerate with `python3 data/build_synthetic.py`.

## Files

| File | What it is |
|---|---|
| `trades.csv` | Front-office bookings |
| `our_confirmations/<id>.txt` | Our confirmation |
| `cpty_confirmations/<id>.txt` | Their confirmation. **T019 and T020 have no file.** |
| `custodian_status.csv` | Custodian view of the cash |
| `ssi_registry.json` | Current instructions, including version history |
| `ssi_snapshot.json` | Cache as of 2026-08-01. Version 2 rows are missing. **v1 reads this.** |
| `bank_directory.csv` | Bank code, institution, branch, country |
| `emails/<id>.txt` | Notice of a new account. Only T007–T010. |
| `scenarios.csv` | Answer key for the v1 / v2 scorecard |

## How to read an instruction

`ssi_registry.json` groups rows by `party`, `currency`, and `purpose`. `history` is oldest first. The row to pay is the last version whose `effective_from` is on or before the trade's `settle_date`.

Two parties have more than one current account at the same bank code:

- Pebble Street Capital, `PINESGSG`: growth `90071001`, income `90071002`
- Lumen Markets, `FNBKUSNY`: operating `90011001`, collateral `90011099`

Same institution, two branches, in `bank_directory.csv`:

- Fable National: New York `FNBKUSNY`, Seoul `FNBKKRSE`
- Pine Custody: Singapore `PINESGSG`, Chicago `PINEUSCH`

## Answer key

`scenarios.csv` is the scorecard. **The agent never reads it, or this README.** Only the scorecard does. Every other file holds only what that party would really know: the custodian expects cash and has a cutoff, nothing more. `expected_decision` is Release or Hold. Same-day breaks stay **Hold** on the scorecard. Urgency is separate: call when the note says so, email otherwise.

| failure_type | trades | v1 mistake | v2 result |
|---|---|---|---|
| `clean` | T001–T006 | Release | Release |
| `stale_ssi` | T007–T010 | Release, because the snapshot still matches both confirms | Hold, fault us |
| `wrong_branch` | T011–T013 | Hold | Hold, fault counterparty |
| `shared_code_wrong_account` | T014–T016 | Hold | Hold |
| `swapped_sides` | T017–T018 | Hold | Hold, fault counterparty |
| `missing_cpty_confirm` | T019–T020 | Crash, no decision | Hold, fault counterparty |

T011, T012, and T014 are written out of order, with mixed date formats, on purpose.
