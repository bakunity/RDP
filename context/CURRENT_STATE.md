# Hermes RDP — Current State Snapshot

Updated: 2026-08-13

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 is merged and accepted.
- PR #20 is merged to `main`; merge commit `dcda9d3890be390a90e9a967905f2cab3c6c7194`.
- Final PR #20 CI #210: Windows PowerShell 5.1 PASS and Linux full release checks PASS.

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

- Live controller/app is deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy returned controller active and `/healthz` OK; rollback anchor `/var/backups/hermes-rdp/controller-20260812T095505Z`.
- Dedicated Hermes sshd PID stayed unchanged during that deploy, so OpenSSH transport was not restarted.
- MIPC accepted Windows agent is `2a170b0f4961299227120afa2eb7c0fffb0f0d13`; later PR #20 commits changed only server bot/registry/tests.

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
- Telegram dashboard auto-refresh and mobile control-button layout.

## Stabilization acceptance

**CP-001 — COMPLETE PASS.** A silent raw TCP client held the API port while five parallel HTTPS `/healthz` requests all succeeded in 16–20 ms; controller and dedicated sshd remained stable. TLS handshake is now per-connection and bounded.

**CL-001 — COMPLETE PASS.** On MIPC, server desired OFF was forced without a new command (`command_seq` remained 27). Agent heartbeat/control stayed alive, converged applied state to OFF, stopped SSH and closed endpoint within 5 seconds. Restoring durable desired ON recovered one SSH process and the endpoint within 8 seconds, still without changing seq.

**CU-001 — COMPLETE PASS.** Existing OSIO OFF seq 14 timed out deterministically after 60 seconds: pending cleared, desired OFF remained durable, timeout result retained seq/action, endpoint stayed closed. Late same-seq result after timeout is rejected by current registry semantics and covered by CI.

**UI-001/UI-002 — COMPLETE PASS.** User confirmed device dashboard updates automatically after command completion without manual Refresh and OFF/RESTART render as separate full-width rows on mobile Telegram.

## Stage 2 current evidence

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. Final Windows process count on the original test machine remains deferred; do not repeat the stress sequence.

**RL-007 — COMPLETE PASS.** Four independent endpoints were previously healthy server-side and passed TCP-through-tunnel checks. Final user-facing acceptance also passed: two simultaneous Microsoft RDP sessions to different Hermes devices were open and usable concurrently without mutual disruption.

**RL-008 — COMPLETE PASS.** Live isolation test forced only MIPC (`:53389`) to durable desired OFF for 12 seconds without changing command sequence. Its listener closed and agent converged to applied OFF / SSH stopped / process count 0. Other healthy Hermes devices retained fresh telemetry and open listeners; controller and dedicated sshd PIDs stayed unchanged. Restoring MIPC desired ON returned one SSH process and open endpoint automatically. User observed the MIPC RDP session drop while the second active RDP session stayed stable and usable throughout.

## Current release gate

Core Stage 2 lifecycle acceptance is now complete except the deferred RL-006 single Windows process-count closure. If the exact original RL-006 test machine is available, only one lightweight `HermesSshCount == 1` check is needed; otherwise move on to device/security lifecycle acceptance.

Do not repeat CP-001, CL-001, CU-001, RL-007, RL-008 or the five-cycle RL-006 stress without a concrete regression reason.
