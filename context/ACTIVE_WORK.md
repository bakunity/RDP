# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, #20, #21, #22, #23 and #24 are merged and accepted.
- PR #22 accepted head: `bc9ee48da570e4d85e1a50cd3b41a631f064609e`; merge commit `ba21a9f969c3ad8ad6760ac423056afb6bb7bd00`.
- PR #23 accepted head: `dd02b63f0b31bc8a64f883c1ab0579ae4e8c96ab`; merge commit `689f80699534d86b98817a17e1c280c26c70e474`.
- PR #24 accepted head: `a5c02747bdfef15128d3e4d31c4c268cb74760f8`; merge commit `f7e3c9e271a75cb2fdc52b564b22f76af47e70d8`.
- CI #266 on PR #24 head: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

## Deployment truth

- Live Linux controller/app remains on accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- Dedicated Hermes tunnel sshd remains separate from admin SSH.
- `SEC005 TEST` remains the non-critical Windows acceptance fixture and is healthy after updater and repair acceptance.

## Stage 4 — Safe migration / updater / rollback

### Server updater — COMPLETE / LIVE-ACCEPTED

- UPD-001: COMPLETE PASS.
- UPD-002 legacy missing-DB backup bug: RESOLVED BY PR #22.
- UPD-003 transactional server updater success path: COMPLETE PASS.
- UPD-004 automatic server rollback: COMPLETE PASS.

### Windows updater — COMPLETE / LIVE-ACCEPTED

- UPD-005 Windows transactional success path: COMPLETE PASS.
- UPD-006 Windows automatic rollback: COMPLETE PASS.

Do not repeat UPD-001..UPD-006 without a concrete updater regression reason.

## Explicit repair engine — COMPLETE / LIVE-ACCEPTED

PR #24 adds bounded local Windows repair for an already-registered device. It deliberately does not perform fresh pairing or automatic rekey.

Accepted behavior:

- existing local identity/config/trust material is required and preserved;
- optional `ExpectedDeviceId` guard prevents repairing the wrong PC;
- existing Ed25519 keypair is validated;
- Win10 x64 + x86 PowerShell/Sysnative native OpenSSH handling is preserved;
- existing pinned API identity and device authentication are checked before mutation;
- immutable candidate is staged/parsed before runtime mutation;
- missing/broken canonical SYSTEM Scheduled Task and agent runtime can be rebuilt;
- RDP service/firewall prerequisites are restored without Defender weakening;
- readiness follows server `desired_enabled`;
- config/key/known-hosts hashes, device ID and RDP port are invariant;
- repair failure restores the previous agent/task snapshot.

### REP-001 — COMPLETE PASS

On `SEC005 TEST`, the harness deliberately removed the local agent file, unregistered the Scheduled Task and stopped Hermes runtime. Exact PR #24 repair returned `REPAIR=PASS`; identity/key/trust hashes and port stayed unchanged, task/runtime were rebuilt, one agent + one matching SSH process recovered, and endpoint reopened.

### REP-002 — COMPLETE PASS

A deliberately different immutable agent candidate was used and a controlled failure was injected immediately after candidate mutation. Product repair emitted `ROLLBACK=PASS`; original agent hash and exact prior Scheduled Task definition were restored; identity/config/key/known-hosts/port stayed unchanged; backup metadata was valid; one agent + one matching SSH process and endpoint recovered. Harness fallback was not needed.

Deliberate current limitation: missing identity/config/private-key/known-hosts material is not silently regenerated. Those cases require a later owner-authorized recovery/rekey endpoint.

## Exact next action

Proceed to **Telegram Repair UX + deterministic pairing retry UX**. Keep `➕ ДОБАВИТЬ ПК` strictly fresh pairing. Add a separate repair action for an existing device that renders a safe local repair command bound to that device ID and immutable repository ref, without embedding device token/private key. Add an explicit expired-pair retry action that generates a new one-time code rather than asking the user to re-run a stale command.

Do not deploy the new server UI until regression tests and CI pass. Do not repeat REP-001/REP-002 without a concrete repair regression reason.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
