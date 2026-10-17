# How a desk actually checks a trade

Generic steps. No employer, no internal system names. This is the checklist Concord's pipeline should follow, in the same order as IDEA.md.

Demo clock is **2026-10-17**.

1. **Open the booking.** One economic trade, with product, sides, amounts, price or rate, and value date. Tool: `load_trade`.
2. **Read our confirmation.** It should repeat the booking and name the account we will pay, or the account that will pay us. Tool: `parse_our_confirmation`.
3. **Read their confirmation.** It should be the mirror, not a copy of our side. If the file is missing, stop and chase. Do not guess. Tool: `parse_counterparty_confirmation`.
4. **Ask the custodian** what cash they expect, in which currency, on which value date. Tool: `get_custodian_status`.
5. **Look up the current instruction**, not the copy saved in a folder. Take the latest version whose effective date is on or before the value date. Tool: `lookup_ssi_registry`.
6. **Resolve the bank code** to an institution, a branch, and a country. The same institution in another city is a different place to send money. Tool: `resolve_bank_branch`.
7. **Check the account, not just the bank.** One code can hold two funds. The purpose on the trade (growth versus income, operating versus collateral) picks the account. Tool: `check_entity_account`.
8. **Cross the sides.** Our pay account is their receive account. Our receive account is their pay account. Two "pay" lines that match each other are a break. Tool: `cross_match_sides`.
9. **Compare the economics.** Amounts, rate or price, currencies, and dates must match across the booking, both confirms, and the custodian. Tool: `compare_economics`.
10. **Price the fail.** For this demo only: a failed settlement costs a flat 5,000 of the cash currency, plus 5 percent a year on the cash amount for each day past value date. That number is made up so the draft can mention a size. Tool: `estimate_fail_cost`.
11. **Decide.** Release only when every check above is clean. Otherwise Hold. Name the fault: us, counterparty, or custodian. Tool: `decide`.
12. **Draft the message** and leave it for a person. Nothing is sent. Tool: `draft_message`.

## Email, or a call

The scorecard in `scenarios.csv` stays **Hold** for every break. Urgency is a second label.

**Call now** when the value date is today (2026-10-17) and the trade is not a clean Release. That is T008, T012, and T019. Say the cash amount and the account that is wrong. Ask them not to release.

**Email is enough** when the value date is two or more days out. Name the field, our value, their value, and the registry value. Ask for an amended confirmation before the value date. Do not threaten. Do not quote a real penalty schedule.

Release trades get no chase message. A one-line "matched, ready to release" note is enough for the queue.
