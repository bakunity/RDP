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
- PR #23 merged; accepted head `dd02b63f0b31bc8a64f883c1ab0579ae4e8c96ab`, merge commit `689f80699534d86b98817a17e1c280c26c70e474`.
- CI #256 on PR #23 head passed Windows PowerShell 5.1 validation and Linux full release checks.

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

- Live Linux controller/app remains deployed from immutable accepted PR #22 head `bc9ee48da570e4d85e1a50cd3b41a631f064609e`.
- Dedicated Hermes sshd remains separate from system/admin sshd.
- The SEC005 test Windows fixture has live-accepted the PR #23 transactional updater and rollback behavior.

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
- PR #22 transactional server updater success + automatic rollback;
- PR #23 transactional Windows updater success + automatic rollback.

## Stage 3 device/security evidence

Stage 3 is COMPLETE. SEC-004 remains intentionally `NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE` because the deleted old-client fixture no longer exists; do not reconstruct credentials merely to manufacture the test.

## Stage 2 deferred item

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. The final one-process check on the exact original Windows device remains optional/deferred; do not repeat the stress sequence.

## Stage 4 updater evidence

**UPD-001 — COMPLETE PASS.** Read-only runtime/source inventory proved healthy immutable deployment baseline.

**UPD-002 — CONFIRMED BUG / RESOLVED.** Legacy server updater backups omitted the live SQLite DB. PR #22 now takes a consistent database snapshot and records rollback provenance.

**UPD-003 — COMPLETE PASS.** Transactional server updater success path live-accepted.

**UPD-004 — COMPLETE PASS.** Deliberate server post-mutation failure triggered automatic rollback and restored ref/config/app/units/database/device state, service health and endpoint listeners.

**UPD-005 — COMPLETE PASS.** Transactional Windows update returned `UPDATE=PASS`; device identity/config/keys/known-hosts/port and Scheduled Task definition were preserved; task/agent/SSH and endpoint were healthy.

**UPD-006 — COMPLETE PASS.** A deliberate Windows post-mutation failure against a different older immutable agent candidate visibly produced `ROLLBACK=PASS`; previous agent hash restored and all independent identity/task/runtime/endpoint checks passed. The harness boolean that attempted to capture `Write-Host` was false because the console host output was not present in that capture variable; this is a harness false negative, not a product rollback failure.

The **server and Windows updater portions of Stage 4 are COMPLETE / LIVE-ACCEPTED**.

## Current release gate

Proceed to **command / pairing / repair UX**:

- keep `Добавить ПК` strictly fresh-pairing and non-destructive for existing installs;
- provide an explicit repair/update flow that preserves current registration, identity, token, Ed25519 keypair, known-hosts and assigned port;
- recover broken/missing local task/agent runtime without silently creating a duplicate device;
- give deterministic expired-pair retry guidance without exposing secret material;
- then finish Russian recovery-state terminology and move toward release docs/v1.2.0 tag.
