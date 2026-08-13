# Hermes RDP — Current State Snapshot

Updated: 2026-08-13

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 merged and accepted.
- PR #20 merged; merge commit `dcda9d3890be390a90e9a967905f2cab3c6c7194`.
- PR #21 merged; merge commit `12ba13080e25e935fb7cc17ece7852005c964c29`.
- PR #22 merged; accepted head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`, merge commit `ba21a9f969c3ad8ad6760ac423056afb6bb7bd00`.
- CI #249 on PR #22 head passed Linux full release checks and Windows PowerShell 5.1 validation.

## Architecture — current

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd :7000
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent public endpoint per device
```

Durable boundaries remain: all Windows machines are equal clients; Linux is infrastructure-special; admin SSH `:22` is independent from Hermes tunnel SSH; FRP is not active runtime; private per-device SSH keys remain on Windows; Telegram is control plane rather than RDP transport.

## Deployment truth

- Live controller/app is deployed from immutable accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- UPD-004 deliberately attempted a post-mutation failure against an older ref and automatically restored this exact accepted live state.
- Dedicated Hermes sshd remains separate from system/admin sshd.
- MIPC accepted Windows agent remains the PR #20 control-first agent.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end / external-network RDP;
- Windows reboot recovery;
- MIPC performance/classification/Observe60;
- Windows Server 2019 acceptance;
- Win10 x64 + PowerShell x86/Sysnative acceptance;
- RL-001..RL-005, RL-007, RL-008;
- CP-001, CL-001, CU-001;
- Telegram dashboard auto-refresh/mobile layout;
- SEC-001, SEC-002, SEC-003, SEC-005, SEC-006, SEC-007, SEC-008;
- PR #21 fresh-install readiness/rollback correction;
- PR #22 transactional server updater success + automatic rollback.

## Stage 3 device/security evidence

Stage 3 is COMPLETE. SEC-004 remains intentionally `NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE` because the deleted old-client fixture no longer exists; do not reconstruct credentials merely to manufacture the test.

## Stage 2 deferred item

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. The final one-process check on the exact original Windows device remains optional/deferred; do not repeat the stress sequence.

## Stage 4 updater evidence

**UPD-001 — COMPLETE PASS.** Read-only runtime/source inventory proved healthy immutable deployment baseline.

**UPD-002 — CONFIRMED BUG / RESOLVED.** Legacy `update-server.sh` backups omitted the live SQLite DB. PR #22 now takes a consistent database snapshot and records rollback provenance.

**UPD-003 — COMPLETE PASS.** Transactional server updater updated production to exact PR #22 head with services/health good, device state and DB metadata preserved, valid SQLite/config/provenance backup created, and all four active endpoint listeners recovered.

**UPD-004 — COMPLETE PASS.** Deliberate post-mutation failure triggered automatic rollback. Ref/config/app/unit hashes, DB ownership/mode, device signature and database integrity were restored; both services, `/healthz`, `hermes-rdpctl doctor` and all prior endpoints recovered. `ROLLBACK=PASS` was reported and no rollback failure was observed.

The **server updater portion of Stage 4 is COMPLETE / LIVE-ACCEPTED**.

## Current release gate

Proceed to **Windows updater / repair hardening**.

Current `scripts/update-client.ps1` is not yet transactional: it stops the healthy task/processes before candidate download, backs up only the agent script, restores only on parse failure, does not restart the old task on that rollback path, has no bounded post-start readiness gate, and has no runtime automatic rollback if a syntactically valid candidate cannot establish a healthy tunnel.

Next implementation must preserve device identity/config/private key/known-hosts/port and Scheduled Task state, stage/parse the candidate before disrupting the working agent where possible, use bounded readiness, and restore the prior agent/task state on activation failure. After regression coverage + CI, run bounded Windows success-path and forced-failure rollback acceptance on a non-critical test device.
