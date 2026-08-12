# Hermes RDP — Current State Snapshot

Updated: 2026-08-12

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 is merged into `main`; reconciled CI #175 passed.

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

- Linux server remains live on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Dedicated sshd and reverse RDP transport remain operational independently of controller failures.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end / external-network RDP;
- Windows reboot recovery;
- MIPC performance/classification/Observe60;
- Windows Server 2019 current-head acceptance;
- Win10 x64 + PowerShell x86/Sysnative current-head acceptance;
- RL-001 Telegram RESTART;
- RL-002 temporary Windows transport loss;
- RL-003 Linux server reboot;
- RL-004 controller restart isolation;
- RL-005 dedicated sshd restart recovery.

## Stage 2 current evidence

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side: old sessions disappeared, new sessions appeared, endpoint listener count stayed exactly one, `:7000` stayed exactly one, controller PID stayed unchanged. Final Windows process count remains deferred; do not repeat the five-cycle stress.

**RL-007 — SERVER-SIDE PASS.** Four independent endpoints (`:53389`, `:53390`, `:53392`, `:53393`) were simultaneously listening and each passed TCP-through-tunnel checks. User-facing dual-RDP completion is paused because soak testing exposed release blockers.

## Confirmed soak-test release blockers

### CP-001 — global HTTPS API stall

After long-lived operation, Telegram showed active machines offline even though reverse SSH endpoint listeners remained alive. `hermes-rdp.service` was still `active` and `:7443` was listening, but local `/healthz` timed out. Forensics showed a saturated listener backlog, an established external connection, and the API thread blocked in socket receive. Telemetry stopped globally while OpenSSH remained healthy.

Root cause boundary: current server wraps the listening HTTP socket in TLS before `ThreadingHTTPServer` dispatches accepted requests, so a stalled TLS handshake can block the accept path.

Controller-only restart restored `/healthz` and active clients resumed telemetry immediately while dedicated sshd stayed untouched.

### CL-001 — desired OFF / local ON command-delivery deadlock

Live reproduced on `пк osio` / `:53390`.

- OSIO telemetry was already stale before OFF was requested.
- OFF set server desired state false and queued seq 14; seq 14 remained pending for many hours.
- Last confirmed command remained seq 13 ON.
- Server endpoint was closed.
- OSIO repeatedly attempted SSH authentication after recovery of the global API.
- The repeatedly rejected Ed25519 fingerprint exactly matched OSIO's registered key.
- Server authorization rejects a device key when desired `enabled=0`.
- Windows agent attempts SSH recovery before telemetry/control polling; failed SSH start aborts the loop before `/telemetry` can fetch pending OFF.

Therefore the device can deadlock: server says OFF and blocks SSH, local state still says ON and keeps retrying SSH, and the agent cannot reach the control poll that would tell it to switch OFF.

### CU-001 — command execution can remain pending indefinitely

OSIO seq 14 stayed pending for hours and Telegram continued displaying an executing command. Deterministic timeout/state semantics are now part of the v1.2.0 stabilization work, but timeout handling must preserve durable desired-state convergence for an offline/recovering device.

## Current release gate

RL-007/RL-008 are paused. Before lifecycle acceptance resumes, v1.2.0 must fix and regression-test:

1. TLS handshake isolation + timeout on API connections;
2. heartbeat/control polling that remains functional when SSH recovery fails;
3. command timeout/status handling without losing desired-state reconciliation.

After CI, server fix is live-validated first, then at least one Windows agent is updated and the former deadlock is reproduced in bounded form.
