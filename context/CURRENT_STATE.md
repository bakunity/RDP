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
- PR #24 merged; accepted head `a5c02747bdfef15128d3e4d31c4c268cb74760f8`, merge commit `f7e3c9e271a75cb2fdc52b564b22f76af47e70d8`.
- CI #266 on PR #24 head passed Windows PowerShell 5.1 validation and Linux full release checks.

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
- The SEC005 test Windows fixture has live-accepted the PR #23 transactional updater and PR #24 repair behavior.

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
- PR #23 transactional Windows updater success + automatic rollback;
- PR #24 bounded Windows repair success + automatic repair rollback.

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

**UPD-006 — COMPLETE PASS.** A deliberate Windows post-mutation failure against a different older immutable agent candidate visibly produced `ROLLBACK=PASS`; previous agent hash restored and all independent identity/task/runtime/endpoint checks passed.

The **server and Windows updater portions of Stage 4 are COMPLETE / LIVE-ACCEPTED**.

## Repair evidence

**REP-001 — COMPLETE PASS.** A controlled fixture removed the agent, Scheduled Task and runtime while preserving registration/trust material. Exact PR #24 repair rebuilt the local runtime and returned `REPAIR=PASS`; identity/trust hashes and port remained unchanged, one agent + one SSH process recovered, and endpoint reopened.

**REP-002 — COMPLETE PASS.** A controlled post-mutation failure against a deliberately different immutable candidate triggered `ROLLBACK=PASS`. Original agent hash and prior Scheduled Task definition were restored; identity/config/key/known-hosts/port stayed unchanged; backup metadata was valid; runtime and endpoint recovered; harness fallback was not needed.

The **bounded local repair engine is COMPLETE / LIVE-ACCEPTED** for cases where local identity/config/private key/known-hosts still exist.

## Current release gate

Proceed to **Telegram repair / pairing retry UX**:

- keep `➕ ДОБАВИТЬ ПК` strictly fresh-pairing;
- add an explicit existing-device Repair action that outputs a safe local repair command bound to the selected device ID and immutable ref, without embedding device secrets;
- add deterministic retry UX for expired one-time pair codes;
- keep missing identity/private-key recovery out of this flow until an explicit owner-authorized recovery/rekey design exists;
- then finish Russian recovery terminology and move toward release docs/v1.2.0 tag.
