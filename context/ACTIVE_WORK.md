# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, #20, #21 and #22 are merged and accepted.
- PR #22 accepted head: `bc9ee48da570e4d85e1a50cd3b41a631f064609e`; merge commit `ba21a9f969c3ad8ad6760ac423056afb6bb7bd00`.
- PR #23 `fix: make Windows updater transactional` is open and mergeable at head `dd02b63f0b31bc8a64f883c1ab0579ae4e8c96ab`.
- CI #256 on PR #23 head: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

## Deployment truth

- Live Linux controller/app remains on accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- Dedicated Hermes tunnel sshd remains separate from admin SSH.
- `SEC005 TEST` is the current non-critical Windows updater acceptance fixture.

## Stage 4 — Safe migration / updater / rollback — ACTIVE

### Server updater — COMPLETE / LIVE-ACCEPTED

- UPD-001: COMPLETE PASS.
- UPD-002 legacy missing-DB backup bug: RESOLVED BY PR #22.
- UPD-003 transactional server updater success path: COMPLETE PASS.
- UPD-004 automatic server rollback: COMPLETE PASS.

### Windows updater

PR #23 stages/parses the candidate before stopping a healthy runtime, resolves to immutable SHA, preserves existing device state and task definition, creates rollback backup metadata, waits for bounded stable runtime readiness, and restores the previous agent on activation failure.

**UPD-005 — COMPLETE PASS.** On `SEC005 TEST`, exact PR #23 updater returned `UPDATE=PASS`; identity/config/key material, known-hosts and assigned port stayed unchanged; task definition stayed unchanged and Running; backup metadata was valid; exactly one agent and one matching SSH process were healthy; endpoint was open.

The first UPD-005 attempt was a harness-only failure: the in-memory ScriptBlock retained the UTF-8 BOM before `param`, so product code never executed or mutated runtime. Retry removed the BOM only from the in-memory harness copy and passed. Classification: HARNESS FAIL / NOT PRODUCT FAIL.

## Exact next action

Run **UPD-006 bounded Windows automatic rollback acceptance** on `SEC005 TEST` using an in-memory temporary copy of exact PR #23 updater with one deliberate failure immediately after candidate activation. The test must prove `ROLLBACK=PASS`, previous agent hash restored, identity/config/key/known-hosts/task definition unchanged, task Running, exactly one agent and one Hermes SSH process, same port and endpoint recovered.

Do not merge PR #23 until UPD-006 passes. Then continue to explicit repair flow / command-pairing-repair UX.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
