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
- PR #21 current head before merge `d1f901a070aa8db006059378d263d7b72214fbb4`; CI #234 COMPLETE PASS.

## Architecture — current

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent public endpoint per device
```

Durable boundaries remain: all Windows machines are equal clients; Linux is infrastructure-special; admin SSH is independent; FRP is not active runtime; private per-device SSH keys remain on Windows; Telegram is control plane rather than RDP transport.

## Deployment truth

- Live controller/app remains deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy returned controller active and `/healthz` OK; dedicated Hermes sshd was not restarted.
- MIPC accepted Windows agent remains the PR #20 control-first agent.
- PR #21 changed Windows fresh-install readiness/rollback behavior and tests; SEC-005 required no production Linux service deploy.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end / external-network RDP;
- Windows reboot recovery;
- MIPC performance/classification/Observe60;
- Windows Server 2019 acceptance;
- Win10 x64 + PowerShell x86/Sysnative acceptance;
- RL-001 Telegram RESTART;
- RL-002 temporary Windows transport loss;
- RL-003 Linux server reboot;
- RL-004 controller restart isolation;
- RL-005 dedicated sshd restart recovery;
- RL-007 simultaneous multi-device user smoke;
- RL-008 one-device failure isolation;
- CP-001 slow/malformed TLS isolation;
- CL-001 desired-state reconciliation independent of SSH transport;
- CU-001 command timeout semantics;
- Telegram dashboard auto-refresh/mobile layout;
- SEC-001 unique per-device identity;
- SEC-002 cross-device SSH/forward isolation;
- SEC-003 hard DELETE/revoke lifecycle;
- SEC-005 deterministic safe released-port reuse and Windows installer retry fix.

## Stage 3 device/security evidence

**SEC-001 — COMPLETE PASS.** Active device inventory showed unique device IDs, API token hashes, Ed25519 keys and RDP ports.

**SEC-002 — COMPLETE PASS.** Each active SSH key maps only to its own `permitlisten` endpoint; an unregistered key was denied and a registered key could not request an unauthorized reverse port.

**SEC-003 — COMPLETE PASS.** Telegram DELETE hard-removed the retired test device; its token hash/key disappeared, old SSH authorization failed, endpoint stayed closed and the port became reusable while MIPC remained healthy.

**SEC-004 — NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE.** No stale deleted-client local identity remained to perform the intended raw old-client replay. Do not reconstruct secrets to manufacture the fixture.

**SEC-005 — RESOLVED / LIVE-ACCEPTED.** Initial clean Windows fresh install exposed a fixed-8-second startup race and stale-local-residue retry bug. PR #21 replaced this with bounded stable-SSH readiness and safe snapshot restoration after confirmed server revoke. CI passed. Live retry created a new identity/key on released port `53391`; task Running; exactly one Hermes SSH; final server post-check showed a sole owner, fresh telemetry, listener/TCP path live, failed/deleted identities not reused and MIPC unaffected. User also connected successfully through Microsoft RDP.

## Stage 2 deferred item

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. Final Windows process count on the original test machine remains optional/deferred; do not repeat the stress sequence.

## Current release gate

Stage 3 remains active. Next gate is **SEC-006 owner-limited Telegram authorization**. Source inspection shows authorization requires both Telegram chat ID and actor ID to equal configured `telegram_chat_id`; unauthorized messages are ignored and unauthorized callbacks receive `Нет доступа`. Run one bounded read-only live-config negative authorization check before marking SEC-006 complete.

After SEC-006, remaining planned security gates are admin SSH `:22` independence from Hermes sshd `:7000` and confirmation that Hermes requires no Defender exclusions/security weakening.
