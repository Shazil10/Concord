# Ninoo screen

Build this at [app.ninoo.ai](https://app.ninoo.ai) with the same Nicrron login. Publish it and paste the `*.ninoo.app` link into the README when it is live.

The real trade data is in `ui/sample_queue.json` (20 trades with decisions, breaks, draft messages). Paste the prompt below into Ninoo Builder.

## Prompt

Build a settlements desk called Concord for a fictional firm, Northline Treasury. Dark, quiet, dense, like an operations screen. No marketing page and no login wall. Nothing is sent to a real network. Approve only adds a row to an outbox on this page.

Screen 1, Queue. Title "Concord". Subtitle "Nothing gets paid until every party agrees." A table of these trades. Columns: trade, product, counterparty, settle date, decision. Decision is a pill: Release in green, Hold in amber.

- T001 FX Lumen Markets 2026-10-17 Release
- T002 FX Kite Rowan Securities 2026-10-21 Release
- T003 BOND Sable Fund Services 2026-10-19 Release
- T004 FX Veldt Capital 2026-10-20 Release
- T005 BOND Quill Asset Management 2026-10-21 Release
- T006 FX Marlow Brothers 2026-10-19 Release
- T007 FX Birch Capital 2026-10-19 Hold
- T008 FX Birch Capital 2026-10-17 Hold
- T009 BOND Holm Securities 2026-10-21 Hold
- T010 FX Holm Securities 2026-10-20 Hold
- T011 FX Orion Desk 2026-10-19 Hold
- T012 BOND Pebble Street Capital 2026-10-17 Hold
- T013 FX Cedar Point Markets 2026-10-22 Hold
- T014 FX Pebble Street Capital 2026-10-19 Hold
- T015 BOND Pebble Street Capital 2026-10-21 Hold
- T016 FX Lumen Markets 2026-10-20 Hold
- T017 FX Kite Rowan Securities 2026-10-19 Hold
- T018 BOND Sable Fund Services 2026-10-21 Hold
- T019 FX Quill Asset Management 2026-10-17 Hold
- T020 BOND Veldt Capital 2026-10-23 Hold

Clicking a Hold row opens Screen 2. Clicking a Release row opens a short "Matched. Ready to release." panel with the same back link.

Screen 2, Trade. Title is the trade id and counterparty, for example "T008 Birch Capital". Under it, one urgency line: if urgency is call, "Settles today. Call, do not wait on email." in red; if email, "Settles <settle date>. Email is enough." in grey. A table of breaks with columns Field, Our value, Their value, Registry. A fault badge: "Fault: us" or "Fault: counterparty". A draft panel with the draft text. Buttons: Approve and Hold. Approve moves the draft into Screen 3 and shows "Held. Not sent." Hold stays on this trade. A back link returns to the queue.

Use exactly this data for each Hold trade (Field | Our value | Their value | Registry; then fault, urgency, draft):

- T007: Account | 90051000 | 90051000 | 90051001. Fault us. Email. Draft: "Birch Capital, your USD account changed on 15 September to 90051001 at Fable National New York. Our confirmation still pays 90051000. We are amending it to 90051001. Please confirm. This note was not sent."
- T008: Account | 90052000 | 90052000 | 90052002. Fault us. Call. Draft: "Birch Capital, your euro account changed on 1 October to 90052002 at Quay and Company, Frankfurt. Our confirmation still pays 90052000. Please confirm before we release. This note was not sent."
- T009: Account | 90061000 | 90061000 | 90061001. Fault us. Email. Draft: "Holm Securities, your USD account changed on 1 August to 90061001 at Westferry Bank, London. Our confirmation still pays 90061000. We are amending it. Please confirm. This note was not sent."
- T010: Account | 90061000 | 90061000 | 90061001. Fault us. Email. Draft: "Holm Securities, same account change as T009. Our confirmation for T010 still pays 90061000. We are amending it to 90061001. Please confirm. This note was not sent."
- T011: Bank code | FNBKUSNY (Fable National New York) | FNBKKRSE (Fable National Seoul) | FNBKUSNY. Fault counterparty. Email. Draft: "Orion Desk, your confirmation names Fable National Seoul. Our registry and our confirmation say Fable National New York, same account. Please send an amended confirmation before value date. This note was not sent."
- T012: Bank code | PINESGSG (Pine Custody Singapore) | PINEUSCH (Pine Custody Chicago) | PINESGSG. Fault counterparty. Call. Draft: "Pebble Street Capital, T012 settles today. Your confirmation names Pine Custody Chicago; the growth account 90071001 is held at Pine Custody Singapore. Please do not release until you amend. This note was not sent."
- T013: Bank code | PINESGSG (Pine Custody Singapore) | PINEUSCH (Pine Custody Chicago) | PINESGSG. Fault counterparty. Email. Draft: "Cedar Point Markets, your confirmation sends our USD to Pine Custody Chicago. Your registered account 90091002 is at Pine Custody Singapore. Please send an amended confirmation. This note was not sent."
- T014: Account | 90071001 (growth) | 90071002 (income) | 90071001 (growth). Fault counterparty. Email. Draft: "Pebble Street Capital, this trade settles to your growth account 90071001. Your confirmation uses the income account 90071002. Please send an amended confirmation. This note was not sent."
- T015: Account | 90071002 (income) | 90071001 (growth) | 90071001 (growth). Fault us. Email. Draft: "Pebble Street Capital, our confirmation pays your income account 90071002 by mistake. This trade settles to the growth account 90071001, as yours says. We are amending ours. This note was not sent."
- T016: Account | 90011099 (collateral) | 90011001 (operating) | 90011001 (operating). Fault us. Email. Draft: "Lumen Markets, our confirmation pays your collateral account 90011099 by mistake. This trade settles to your operating account 90011001, as yours says. We are amending ours. This note was not sent."
- T017: Sides | We pay 90021001, receive 90020001 | They pay 90020001, receive 90021001 | We pay 90021001. Fault counterparty. Email. Draft: "Kite Rowan Securities, your confirmation has the two legs swapped: it says you pay USD and receive EUR, the same direction as ours. Please send a corrected confirmation. This note was not sent."
- T018: Sides | We pay 90031001, receive 90010001 | They pay 90010001, receive 90031001 | We pay 90031001. Fault counterparty. Email. Draft: "Sable Fund Services, your confirmation says you pay the cash and we deliver the bond. We are buying the bond and paying USD. Please send a corrected confirmation. This note was not sent."
- T019: Confirmation | Sent | None received | —. Fault counterparty. Call. Draft: "Quill Asset Management, T019 settles today and we have not received your confirmation. Please send it now; we will not release until it matches. This note was not sent."
- T020: Confirmation | Sent | None received | —. Fault counterparty. Email. Draft: "Veldt Capital, we have not received your confirmation for T020, value 23 October. Please send it so we can match before value date. This note was not sent."

Screen 3, Outbox. A list of notes sitting on this desk. Empty until Approve is clicked. Each row shows the trade id, the counterparty, and the words "Not sent".

Keep every name and account fictional. Do not add a send button.
