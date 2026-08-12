# Hermes RDP — Active Work

Updated: 2026-08-12

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 is merged into `main`; reconciled CI #175 passed.

## Deployment truth

- Linux server remains live on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Dedicated OpenSSH transport is operational and remains isolated from controller lifecycle.

## Stable accepted blocks

Do not repeat without a concrete regression reason:

- OpenSSH reverse RDP end-to-end and external-network RDP;
- Windows reboot recovery;
- Telegram OFF/ON and endpoint CLOSED/OPEN truth on the accepted healthy path;
- MIPC current-head performance/classification/Observe60 acceptance;
- Windows Server 2019 current-head acceptance;
- Win10 x64 + PowerShell x86/Sysnative current-head acceptance;
- RL-001 Telegram RESTART recovery;
- RL-002 temporary Windows-side transport loss recovery;
- RL-003 Linux server reboot recovery;
- RL-004 controller restart isolation;
- RL-005 dedicated sshd restart recovery.

## Stage 2 evidence accumulated

### RL-006 repeated reconnect stress — PARTIAL PASS

Five consecutive dedicated-sshd restart cycles each removed the old endpoint session, created a different new `sshd-session`, returned exactly one listener on the tested endpoint and exactly one listener on `:7000`, and left the controller PID unchanged. Server side is PASS. Final Windows `ssh.exe` count was not collected because the RDP client later became unusable; do not repeat the five-cycle stress. When that Windows machine is available, only one final process-count check is needed.

### RL-007 multi-device — SERVER-SIDE PASS

Four independent endpoint listeners were simultaneously present on `:53389`, `:53390`, `:53392`, and `:53393`. TCP checks through all four endpoints passed while dedicated sshd remained healthy. User-facing simultaneous dual-RDP smoke was interrupted by newly discovered lifecycle defects below.

## Release blockers discovered by soak / long-lived operation

### CP-001 — HTTPS API accept path can stall on TLS handshake — CONFIRMED BUG

After roughly a day of operation, Telegram showed all active devices offline while multiple OpenSSH endpoint listeners remained alive. Live forensics showed:

- `hermes-rdp.service` still `active` and `:7443` still LISTEN;
- local `/healthz` timed out;
- listener backlog reached `Recv-Q 6 / backlog 5`;
- an external connection remained established on `:7443`;
- the API thread was blocked in socket receive (`tcp_recvmsg`);
- Windows telemetry stopped globally while independent OpenSSH tunnels remained alive.

Current server code wraps the listening HTTP socket in TLS before `ThreadingHTTPServer` can hand accepted connections to worker threads, so a stalled TLS handshake can block the accept path.

Controller-only restart recovered the API without restarting dedicated sshd. `/healthz` immediately passed and active Windows clients resumed telemetry with `last_seen` age about one second.

**v1.2.0 release blocker:** TLS handshake must be isolated per accepted connection and bounded by timeout; one slow/malformed client must never block global API acceptance.

### CL-001 — desired OFF + local ON can deadlock command delivery — CONFIRMED BUG

Live reproduced on device `пк osio` / endpoint `:53390`:

- device had already stopped telemetry long before the OFF button was pressed;
- Telegram OFF stored desired access OFF and queued command seq 14;
- pending `off` remained unresolved for many hours; last confirmed result remained seq 13 `on`;
- server endpoint was CLOSED;
- Windows continued repeatedly attempting SSH authentication;
- the repeated SSH fingerprint exactly matched OSIO's registered Ed25519 key;
- server rejected that key because `authorize_ssh_key()` permits only devices with `enabled=1`;
- Windows agent attempts transport reconciliation before posting telemetry, so failed `Start-SshTunnel` aborts that loop iteration before it can fetch the pending OFF command.

This creates a control deadlock: server desired OFF blocks SSH, local agent still believes ON, SSH start fails, heartbeat/control poll is skipped, pending OFF is never received.

**v1.2.0 release blocker:** heartbeat/control polling must remain functional even when tunnel start/recovery fails. Transport reconciliation cannot gate telemetry/control delivery.

### CU-001 — pending command can remain "executing" indefinitely — CONFIRMED UX/STATE BUG

OSIO command seq 14 remained pending for many hours with no result, and Telegram continued showing execution in progress. Deterministic timeout/state handling is now promoted from later UX work into the stabilization fix. Timeout semantics must not break durable desired-state reconciliation for offline devices.

## Exact next action

Pause RL-007/RL-008 acceptance and implement a dedicated stabilization fix branch covering:

1. per-connection TLS handshake with bounded timeout so API accept remains available;
2. Windows agent heartbeat/control path independent from SSH start/recovery failure;
3. safe command timeout/status semantics that preserve durable desired state;
4. regression tests for both confirmed deadlocks/stalls.

After CI, deploy server fix first, update at least one Windows agent, reproduce the previously failing conditions in bounded form, then resume RL-007/RL-008.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
