# Hermes RDP — Session Protocol

## Goal

Make every engineering chat resumable without relying on memory or repeating already accepted tests.

## Start of session

Read in this order:

1. `context/LAST_SESSION.md`;
2. `context/ACTIVE_WORK.md`;
3. `context/CURRENT_STATE.md`;
4. `context/NEXT_WORK.md`;
5. `context/EVIDENCE_LEDGER.md`;
6. `context/DECISIONS.md` when architecture choices matter;
7. `context/archive/` only when detailed historical audit/provenance is needed.

Then reconcile current `main`, latest release, open PRs/branches and CI with the saved context before changing anything.

## During work

- Work one bounded stage at a time.
- Preserve immutable commit SHA provenance for live acceptance.
- Do not repeat a PASS without a concrete regression reason.
- Treat Windows PowerShell 5.1 and Win10 x64+x86/Sysnative compatibility as product requirements.
- Keep certificate work out of the main 3-second Agent loop.
- Use disposable fixtures for destructive install/uninstall gates when a trusted long-lived fixture should be preserved.
- Never put secrets into chat/context/release notes.

## Evidence

Record:

- exact accepted code SHA;
- CI run/result;
- fixture identity only when useful for provenance;
- the smallest set of output markers needed to prove the acceptance boundary;
- confirmed bugs/root causes and rollback result;
- what must not be repeated.

A later docs/context-only commit does not invalidate an earlier product/test code acceptance boundary. A later relevant product-code change does.

## Release ledger

As work becomes release-relevant, update `docs/releases/UNRELEASED.md` immediately.

For a version cut:

- public GitHub Release notes: compact `docs/releases/vX.Y.Z.md`;
- detailed history: `docs/releases/history/vX.Y.Z-full.md`;
- do not reconstruct the release from memory at the end.

## Before chat migration / handoff

Update at minimum:

- `LAST_SESSION.md`;
- `ACTIVE_WORK.md`;
- `CURRENT_STATE.md`;
- `NEXT_WORK.md`;
- `EVIDENCE_LEDGER.md` when acceptance/root-cause state changed.

Also update `DECISIONS.md`, `HISTORY.md`, `PROJECT_HANDOFF.md` and `UNRELEASED.md` when their durable boundary changed.

The handoff must state the exact next action, the latest accepted SHA, current PR/merge status and tests that must not be repeated.

## Current protocol example

CERT-013 accepted product/test code head is `e11cf89ed26d551ca92b4010034d6e6792a9266b`; CI #381 passed Linux + Windows PowerShell 5.1; live Update, Repair, clean Fresh Install, external trusted RDP and Uninstall are accepted. Evidence/context-only commits after that SHA do not require rerunning those product tests.
