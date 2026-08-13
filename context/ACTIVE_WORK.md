# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 through PR #25 are merged and accepted.
- PR #24 accepted head: `a5c02747bdfef15128d3e4d31c4c268cb74760f8`; merge commit `f7e3c9e271a75cb2fdc52b564b22f76af47e70d8`.
- PR #25 accepted head: `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`; merge commit `0077efd59394a815385ecbf3940b851039e40f1d`.
- CI #272 on PR #25 head: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

## Deployment truth

- Live Linux controller/app is deployed from exact accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60` via the transactional server updater; deployment returned `UPDATE=PASS` and created a rollback backup.
- Dedicated Hermes tunnel sshd remains separate from admin SSH.
- `SEC005 TEST` remains healthy after updater, repair success/rollback acceptance and final Microsoft RDP smoke.

## Stage 4 — Safe migration / updater / rollback — COMPLETE

- UPD-001..UPD-006: COMPLETE / LIVE-ACCEPTED.
- Do not repeat without a concrete updater regression reason.

## Explicit repair engine — COMPLETE / LIVE-ACCEPTED

PR #24 provides bounded local Windows repair for an already-registered device. It preserves existing config, device identity, Ed25519 keypair, known-hosts and RDP port; can rebuild the canonical SYSTEM Scheduled Task/agent runtime; and rolls back the previous local runtime snapshot on failure.

- REP-001 missing agent/task recovery: COMPLETE PASS.
- REP-002 forced post-mutation failure rollback: COMPLETE PASS.
- Final ordinary Microsoft RDP connection after both tests: PASS.

Deliberate limitation remains: missing local identity/config/private-key/known-hosts material is not silently regenerated; that requires a separate owner-authorized recovery/rekey design.

## Telegram repair / pairing UX — COMPLETE / LIVE-ACCEPTED

PR #25 keeps fresh pairing and existing-device repair explicitly separate.

- UX-001 existing-device repair screen: COMPLETE PASS. Telegram renders the selected device, endpoint, immutable repair command, device-ID guard and complete parameter invocation without embedding device token/private key.
- UX-002 pairing retry/new-code behavior: COMPLETE PASS. `НОВЫЙ КОД` creates a different one-time code and the rendered installer command updates to the same new value.
- No pairing code or other secret material is stored in durable context.

## Exact next action

Proceed to the **v1.2.0 release-prep pass**: review Russian recovery/edge-state terminology, reconcile user-facing docs with the accepted OpenSSH/updater/repair/Telegram UX model, and prepare release notes/tagging without reopening completed live tests.

RDP trusted-certificate work is a separate planned track after the release-prep pass: bind a hostname-matching certificate to the Windows RDP listener; HTTPS certificate configuration alone does not replace the RDP listener certificate.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
