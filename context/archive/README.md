# Hermes RDP — Context Archive

This directory stores **historical/superseded material that is useful to retain but must not participate in normal current-state reasoning**.

Read current context first:

1. `../README.md`
2. `../ACTIVE_WORK.md`
3. `../EVIDENCE_LEDGER.md`
4. `../CURRENT_STATE.md`

Only enter this archive when old reasoning/evidence is specifically needed.

## Archive rules

Every new archive snapshot should make its status obvious near the top:

```text
Status: HISTORICAL / SUPERSEDED
Captured: YYYY-MM-DD
Superseded by: <current file / decision / release>
Reason retained: <why this history may still matter>
```

Archive material never overrides current runtime evidence or current context.

## What belongs here

- deep audits replaced by newer audits;
- release evidence snapshots after ledger compaction;
- major architecture/migration rationale that was superseded;
- incident/root-cause reports worth preserving;
- unusually valuable full reasoning snapshots.

## What does not belong here

- every chat;
- every terminal command;
- temporary debug output;
- routine completed TODOs;
- duplicate copies of current context;
- secrets or production-sensitive values.

Git history is the normal way to recover ordinary previous versions of active context files.

## Naming

Prefer:

```text
YYYY-MM-DD-<topic>-audit.md
YYYY-MM-DD-<topic>-incident.md
releases/vX.Y.Z-evidence.md
```

## Current known snapshots

- `2026-08-07-full-product-audit.md` — historical full product audit from the initial long stabilization analysis. Some TODOs in it were later resolved; do not treat its status matrix as current.

Update this short index when a deliberately retained archive snapshot is added. Do not turn the index into another history log.