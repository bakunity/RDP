# Hermes RDP — Active Work

Updated: 2026-08-13

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 through PR #25: merged / runtime accepted.
- PR #26: merged; documentation reconciliation complete. Merge commit `b3e49e9caff0229ce9f626094393fbf1692878de`.
- PR #27: draft final release PR on branch `release-v1.2.0`.
- PR #27 CI #279: Linux full release checks PASS; Windows PowerShell 5.1 validation PASS.

## Deployment truth

- Live Linux controller/app remains deployed from exact accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`.
- Production runtime is not changed by PR #26 or unmerged PR #27.
- `SEC005 TEST` remains healthy after updater, repair and final Microsoft RDP acceptance.

## Completed stabilization scope

- Stage 3 device/security: COMPLETE, except SEC-004 remains fixture-unavailable by design.
- Stage 4 server + Windows transactional updater: COMPLETE / LIVE-ACCEPTED.
- Explicit Windows Repair engine: COMPLETE / LIVE-ACCEPTED.
- Telegram Repair + new pairing-code UX: COMPLETE / LIVE-ACCEPTED.
- Do not repeat completed live tests without a concrete regression reason.

## Current release gate

PR #27 synchronizes version metadata to `1.2.0`, adds final release-note path, updates CHANGELOG/README release status and retires the temporary v1.2 draft.

The branch passes CI, but PR #27 intentionally remains **draft / unmerged** because merging it may trigger the repository release workflow and publish/tag `v1.2.0`.

**Next action requires explicit final release approval:** mark PR #27 ready, merge exact accepted head, then verify the generated `v1.2.0` tag/GitHub Release and release links.

RDP trusted-certificate work remains a separate post-release track.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
