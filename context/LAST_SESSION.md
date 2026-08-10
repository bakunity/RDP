# Hermes RDP — Last Session Handoff

Updated: 2026-08-08
Status: **COMPACTED / NON-AUTHORITATIVE**

`LAST_SESSION.md` is no longer the primary project memory.

The original 2026-08-07 long-session handoff became stale after subsequent stabilization work. Its durable facts have been promoted into:

- `ACTIVE_WORK.md` — current operational state and exact next step;
- `EVIDENCE_LEDGER.md` — confirmed PASS/FAIL/root-cause evidence;
- `CURRENT_STATE.md` — consolidated product truth;
- `NEXT_WORK.md` — remaining work;
- `HISTORY.md` — significant milestones.

Do **not** use the old 2026-08-07 handoff wording to infer current bugs, TODOs, PR state or deployment state. Git history preserves that previous version if historical reconstruction is needed.

## Current handoff rule

This file is rewritten only when intentionally pausing/moving a long chat and there is a short boundary delta not already obvious from HOT context.

A boundary handoff should contain only:

- where work paused;
- any immediate caveat that is easy to miss;
- exact resume action if different from `ACTIVE_WORK.md`.

If no unique boundary delta exists, keeping this compact pointer is preferable to duplicating `ACTIVE_WORK.md`.

For current project work, start with `context/README.md`.