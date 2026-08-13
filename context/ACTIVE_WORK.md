# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs in the evidence/history files.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, PR #20, PR #21 and PR #22 are merged and accepted.
- PR #22 title: `fix: make server updater transactional`.
- PR #22 accepted head: `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- PR #22 merge commit: `ba21a9f969c3ad8ad6760ac423056afb6bb7bd00`.
- CI #249 on the accepted PR #22 head: Linux PASS and Windows PowerShell 5.1 PASS.

## Deployment truth

- Live controller/app remains deployed from immutable PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- The bounded UPD-004 forced-failure test rolled back to that same accepted live state.
- Dedicated `hermes-rdp-sshd.service` remains separate from admin SSH.
- MIPC accepted Windows agent remains the PR #20 control-first agent.

## Completed stabilization evidence retained

- Stage 2 lifecycle: RL-001..RL-005, RL-007 and RL-008 COMPLETE PASS; RL-006 remains PARTIAL only for the optional exact-machine final one-process count.
- Stage 3 device/security: COMPLETE; SEC-004 remains fixture-unavailable rather than falsely live-tested.
- PR #21 fresh-install readiness/retry rollback: RESOLVED / LIVE-ACCEPTED.

## Stage 4 — Safe migration / updater / rollback — ACTIVE

### Server updater — COMPLETE / LIVE-ACCEPTED

**UPD-001 — COMPLETE PASS.** Read-only production inventory proved healthy immutable baseline and exposed the legacy backup boundary.

**UPD-002 — CONFIRMED BUG / RESOLVED BY PR #22.** Legacy `update-server.sh` backups did not include `/var/lib/hermes-rdp/state.sqlite3`.

**UPD-003 — COMPLETE PASS.** Exact PR #22 head updated production successfully. Both Hermes services and `/healthz` were healthy, device state and DB metadata stayed unchanged, consistent SQLite/config/provenance backup was created, and all four active endpoint listeners recovered.

**UPD-004 — COMPLETE PASS.** A temporary local updater copy injected a deliberate post-mutation failure while targeting an older immutable ref. Automatic rollback reported `ROLLBACK=PASS` and restored repository ref, config/app/unit hashes, DB ownership/mode, device-state signature, database integrity, service health, `hermes-rdpctl doctor`, and all prior endpoint listeners.

PR #22 was merged only after CI plus UPD-003 and UPD-004 passed.

### Windows updater / repair — CURRENT GATE

The existing `scripts/update-client.ps1` still has weaker recovery semantics than the now-accepted server updater. Source inventory established that it:

- backs up only `HermesRdpAgent.ps1`;
- stops the Scheduled Task and Hermes processes before downloading the replacement agent;
- restores the old agent only for PowerShell parse errors;
- does not restart the old task on that parse-error rollback path;
- has no bounded runtime-readiness gate after `Start-ScheduledTask`;
- has no automatic rollback if the new agent parses but fails to establish a healthy Hermes tunnel;
- has no explicit repair entry point distinct from update/install.

## Exact next action

Proceed with **Windows updater/repair hardening** before any destructive Windows live test.

First design a transactional `update-client.ps1` boundary that preserves device identity/config/private key/known-hosts/port and existing task definition, downloads and validates the candidate before stopping the working agent where possible, uses bounded readiness after activation, and automatically restores the previous agent/task state if activation fails.

Then add regression coverage and CI. Only after that should a bounded live Windows success-path and forced-failure rollback test run on a non-critical test device.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
