# Pitch — Concord

Say this. Do not open a slide deck, and do not show any employer document.

## 20 seconds

Analysts check one trade by hand across the booking, our confirmation, their confirmation, the custodian, and the account instruction. The instruction in the folder is not always the instruction that is current. One old account number sends the cash to the wrong place. Whoever caused it pays the fail. Concord reads all five before the cash moves, and it leaves a person one decision: approve.

## Three minutes, with Shazil

1. **Problem, 20s.** The paragraph above. Use T008: Birch changed its euro account on 1 October. Both confirmations still show the old one. It settles today.
2. **Screen, 40s.** Open the queue. Five other trades are Release. Open T008. Show the old account, the registry account, the draft note, then Hold. The note lands in the outbox. Nothing is sent.
3. **Steps, 20s.** Shazil opens that same run. Twelve tool calls, one after another.
4. **Failure, 30s.** v1 released T007, T008, T009, and T010 because it read the saved instructions. The cluster says why: the agent trusted a cache.
5. **Fix, 30s.** Same files, v2. Those four are Hold. The scorecard is the difference.
6. **Alert, 20s.** T019 has no counterparty confirmation and settles today. v1 dies with no decision. The error-rate alert fires. v2 Holds and chases.
7. **Vision, 20s.** The accounts should live in one shared instruction layer that every party can rely on. Concord is the check on top of that layer: latest version, right branch, right account, right side, then a human signs.

## Line we already agreed

We work in World Bank Group Treasury, in trade operations and financial technology. Every day trades are checked field by field across five systems before money moves. Concord does that check, explains every break, and leaves the human one decision: approve.
