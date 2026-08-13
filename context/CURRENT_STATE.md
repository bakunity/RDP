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
- PR #22 `fix: make server updater transactional` is open, mergeable, current head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`; CI #249 passed Linux and Windows PowerShell 5.1 validation.

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

- Live controller/app is deployed from immutable PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e` after successful transactional-updater live acceptance.
- Previous live repository ref was `77240e2d758f0ed4598553d4d903331229653f06`.
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
- UPD-003 transactional server updater success path on PR #22 head.

## Stage 3 device/security evidence

Stage 3 is COMPLETE. SEC-004 remains intentionally `NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE` because the deleted old-client fixture no longer exists; do not reconstruct credentials merely to manufacture the test.

## Stage 2 deferred item

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. The final one-process check on the exact original Windows device remains optional/deferred; do not repeat the stress sequence.

## Stage 4 updater evidence

**UPD-001 — COMPLETE PASS.** Read-only runtime/source inventory proved healthy immutable deployment baseline.

**UPD-002 — CONFIRMED BUG.** Legacy `update-server.sh` backups did not include the live SQLite DB, so rollback state was incomplete.

**UPD-003 — COMPLETE PASS.** PR #22 transactional updater successfully updated production from `77240e2d...` to exact head `bc9ee48d...`; services and health stayed good after restart, device state and DB metadata were preserved, rollback backup now includes a valid SQLite snapshot plus old config and provenance metadata, and all four active endpoint listeners recovered.

## Current release gate

Run **UPD-004 bounded automatic rollback acceptance** before merging PR #22. Use a temporary local copy of the exact updater with a deliberate test-only failure inserted after deployment mutation. Acceptance requires automatic rollback to restore current ref/config, app/unit hashes, DB/device state and permissions, both Hermes services/health, and endpoint listeners.

After UPD-004 passes, continue with Windows updater/repair hardening and live acceptance, then command/pairing/repair UX, release docs and the v1.2.0 immutable tag.
