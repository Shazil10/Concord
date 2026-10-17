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

Screen 2, Trade, using T008 as the example. Title "T008 Birch Capital". Line: "Settles today. Call, do not wait on email." A table of breaks with columns Field, Our value, Their value, Registry. One row: Account, 90052000, 90052000, 90052002. Fault: us. A draft panel with this text: "Birch Capital, your euro account changed on 1 October to 90052002 at Quay and Company, Frankfurt. Our confirmation still pays 90052000. Please confirm before we release. This note was not sent." Buttons: Approve and Hold. Approve moves the draft into Screen 3 and shows "Held. Not sent." Hold stays on this trade.

Screen 3, Outbox. A list of notes sitting on this desk. Empty until Approve is clicked. Each row shows the trade id, the counterparty, and the words "Not sent".

Keep every name and account fictional. Do not add a send button.
