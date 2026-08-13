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
- PR #24 `feat: add bounded Windows repair flow` is open and mergeable at head `a5c02747bdfef15128d3e4d31c4c268cb74760f8`.
- CI #266 on PR #24 head: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

## Deployment truth

- Live Linux controller/app remains on accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- Dedicated Hermes tunnel sshd remains separate from admin SSH.
- `SEC005 TEST` remains the non-critical Windows acceptance fixture and is healthy after updater and REP-001 repair acceptance.

## Stage 4 — Safe migration / updater / rollback

### Server updater — COMPLETE / LIVE-ACCEPTED

- UPD-001: COMPLETE PASS.
- UPD-002 legacy missing-DB backup bug: RESOLVED BY PR #22.
- UPD-003 transactional server updater success path: COMPLETE PASS.
- UPD-004 automatic server rollback: COMPLETE PASS.

### Windows updater — COMPLETE / LIVE-ACCEPTED

- UPD-005 Windows transactional success path: COMPLETE PASS.
- UPD-006 Windows automatic rollback: COMPLETE PASS.

PR #23 was merged only after CI, UPD-005 and UPD-006 acceptance. Do not repeat UPD-001..UPD-006 without a concrete updater regression reason.

## Explicit repair flow — ACTIVE

PR #24 adds the first bounded local Windows repair engine for an already-registered device. The repair boundary intentionally does not perform fresh pairing or automatic rekey.

Current PR #24 behavior:

- requires existing `device.json`, device registration/trust material and local Ed25519 keypair;
- optional `ExpectedDeviceId` guard prevents repairing the wrong local Hermes identity;
- validates the local Ed25519 keypair;
- preserves Win10 x64 + x86 PowerShell/Sysnative native OpenSSH handling;
- pins/authenticates the existing API identity before mutation;
- resolves/stages/parses an immutable candidate before stopping runtime;
- can rebuild a missing/broken canonical SYSTEM Scheduled Task and agent runtime;
- restores RDP service/firewall prerequisites without Defender weakening;
- requires bounded stable agent/SSH state according to server `desired_enabled`;
- verifies config/key/known-hosts hashes plus device ID/RDP port remain unchanged;
- restores the previous agent/task snapshot on repair failure.

Deliberate current limitation: missing identity/config/private-key/known-hosts material is not silently regenerated. Those cases require a later owner-authorized recovery/rekey endpoint.

### REP-001 — COMPLETE PASS

On `SEC005 TEST`, a healthy baseline first showed the Scheduled Task Running, exactly one Hermes agent process, exactly one matching `ssh.exe`, and the public endpoint open. The harness then deliberately removed the local agent file, unregistered the Scheduled Task, and stopped the Hermes runtime.

Exact PR #24 repair returned `REPAIR=PASS` on immutable head `a5c02747bdfef15128d3e4d31c4c268cb74760f8`. Independent post-check proved:

- config/key/known-hosts hashes and device identity unchanged;
- assigned RDP port unchanged;
- repair backup metadata valid;
- Scheduled Task rebuilt and Running;
- exactly one agent and one matching Hermes SSH process;
- endpoint recovered and open.

## Exact next action

Run **REP-002 bounded forced-failure repair rollback acceptance** on `SEC005 TEST`. Inject one controlled failure after repair mutation using only an in-memory temporary copy of exact PR #24 repair logic, then prove the previous agent/task state is restored, identity/config/key/known-hosts/port remain unchanged, one agent + one Hermes SSH process recover, and endpoint is open.

Do not merge PR #24 until REP-002 passes. Do not repeat REP-001 without a concrete repair regression reason.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
