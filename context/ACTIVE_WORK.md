# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, #20, #21, #22 and #23 are merged and accepted.
- PR #22 accepted head: `bc9ee48da570e4d85e1a50cd3b41a631f064609e`; merge commit `ba21a9f969c3ad8ad6760ac423056afb6bb7bd00`.
- PR #23 accepted head: `dd02b63f0b31bc8a64f883c1ab0579ae4e8c96ab`; merge commit `689f80699534d86b98817a17e1c280c26c70e474`.
- CI #256 on PR #23 head: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

## Deployment truth

- Live Linux controller/app remains on accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- Dedicated Hermes tunnel sshd remains separate from admin SSH.
- `SEC005 TEST` is the non-critical Windows updater acceptance fixture and remains healthy after update/rollback acceptance.

## Stage 4 — Safe migration / updater / rollback

### Server updater — COMPLETE / LIVE-ACCEPTED

- UPD-001: COMPLETE PASS.
- UPD-002 legacy missing-DB backup bug: RESOLVED BY PR #22.
- UPD-003 transactional server updater success path: COMPLETE PASS.
- UPD-004 automatic server rollback: COMPLETE PASS.

### Windows updater — COMPLETE / LIVE-ACCEPTED

- UPD-005 Windows transactional success path: COMPLETE PASS.
- UPD-006 Windows automatic rollback: COMPLETE PASS.

UPD-006 used a deliberately different older immutable agent candidate and an injected post-mutation failure. The updater visibly emitted `ROLLBACK=PASS`; previous agent hash, device identity/config, Ed25519 key material, known-hosts, Scheduled Task definition and assigned port were restored/preserved; task returned Running; exactly one agent and one matching SSH process remained; backup metadata was valid; endpoint was reachable.

The surrounding PowerShell 5.1 harness printed `RollbackReportedPass=False` because `Write-Host` output was visible in the console but not captured into the variable used by that assertion. All independent rollback checks passed. Classification: HARNESS OBSERVATION FALSE NEGATIVE / PRODUCT PASS.

PR #23 was merged only after CI, UPD-005 and UPD-006 acceptance.

## Exact next action

Proceed to **explicit repair flow / command-pairing-repair UX**. Keep `Добавить ПК` as fresh pairing only. Design a separate repair/update path that preserves existing registration and secret material, can recover missing/broken task or agent runtime without creating a second device, and gives clear retry guidance for expired pairing codes.

Do not re-run UPD-001..UPD-006 without a concrete updater regression reason.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
