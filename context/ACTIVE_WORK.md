# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs in the evidence/history files.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, PR #20 and PR #21 are merged and accepted.
- PR #22 `fix: make server updater transactional` is open and mergeable.
- PR #22 current head: `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- CI #249 on that head: Linux PASS and Windows PowerShell 5.1 PASS.

## Deployment truth

- Live controller/app is now deployed from immutable PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e` via the new transactional updater success path.
- Previous live repository ref before that update was `77240e2d758f0ed4598553d4d903331229653f06`.
- Dedicated `hermes-rdp-sshd.service` remains separate from admin SSH.
- MIPC accepted Windows agent remains the PR #20 control-first agent.
- PR #21 changed Windows fresh-install readiness/rollback behavior and required no Linux service deploy.

## Stage 2 lifecycle

- RL-001..RL-005: COMPLETE PASS.
- RL-006: PARTIAL PASS; five-cycle server-side reconnect stress passed, with only the optional original-machine one-process check uncollected.
- RL-007: COMPLETE PASS.
- RL-008: COMPLETE PASS.

## Stage 3 — Device / Security lifecycle — COMPLETE

- SEC-001 unique per-device identity: COMPLETE PASS.
- SEC-002 cross-device SSH/forward isolation: COMPLETE PASS.
- SEC-003 hard DELETE/revoke lifecycle: COMPLETE PASS.
- SEC-004 stale deleted-client reclaim: NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE; do not reconstruct credentials to manufacture this test.
- SEC-005 deterministic released-port reuse: RESOLVED / LIVE-ACCEPTED through PR #21.
- SEC-006 owner-limited Telegram authorization: COMPLETE PASS.
- SEC-007 admin SSH `:22` vs Hermes sshd `:7000` independence: COMPLETE PASS.
- SEC-008 no Windows security weakening: COMPLETE PASS with normal Defender real-time/behavior protection enabled and no Hermes/broad exclusions; the Hermes RDP session remained usable throughout the final protection-enable acceptance.

## Stage 4 — Safe migration / updater / rollback — ACTIVE

### UPD-001 runtime/source baseline — COMPLETE PASS

Read-only production inventory established:

- configured repository ref was immutable `77240e2d758f0ed4598553d4d903331229653f06`;
- controller and dedicated tunnel sshd were active;
- `/healthz` returned 200;
- SQLite DB existed and runtime was healthy;
- five historical `update-*` backups existed;
- deployment has no local Git metadata, so config provenance is the operative deployment source record.

### UPD-002 legacy updater backup boundary — CONFIRMED BUG

The latest pre-PR22 updater backup contained `/opt/hermes-rdp` and config but **did not contain `/var/lib/hermes-rdp/state.sqlite3`**. The old updater therefore did not provide a complete state rollback anchor even though operations documentation requires database backup.

### PR #22 hardening — IMPLEMENTED / CI PASS

PR #22 now:

- resolves requested ref to an exact commit SHA before download;
- records the resolved SHA as `repository_ref` and the requested ref separately;
- pins the Windows installer URL to the resolved SHA;
- creates a consistent SQLite backup with `sqlite3.Connection.backup()` plus `PRAGMA quick_check`;
- writes non-secret update metadata into the rollback backup;
- arms automatic rollback before the first deployment mutation;
- restores app/config/units/database on post-mutation failure;
- gates success on services, `/healthz`, `hermes-rdpctl doctor`, sshd config validation and DB quick-check.

### UPD-003 transactional updater success path — COMPLETE PASS

Live update from `77240e2d...` to exact PR #22 head `bc9ee48d...` completed with `UPDATE=PASS`.

Post-check proved simultaneously:

- configured ref changed to the exact target SHA;
- both Hermes services healthy and `/healthz=200`;
- device registry signature unchanged;
- live DB owner/group/mode unchanged;
- rollback backup contains app/config/database/update metadata;
- backup DB `PRAGMA quick_check` passed;
- backup metadata correctly records target and previous ref;
- backup config contains the previous deployment ref;
- all four pre-update active endpoint listeners recovered;
- both controller and dedicated sshd restarted as expected.

## Exact next action

Run **UPD-004 bounded automatic rollback acceptance** using a temporary copy of the exact PR #22 updater with one deliberate local fault injected after deployment mutation and before success commit. The test must prove automatic rollback restores:

- the current `bc9ee48d...` repository ref/config;
- app/unit hashes;
- database/device state and permissions;
- controller + dedicated sshd health;
- endpoint listeners.

Do not merge PR #22 until UPD-004 rollback acceptance passes. After server updater rollback is live-accepted, harden and test the Windows updater/repair path.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
