# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 is merged and accepted.
- PR #20 (`fix: prevent soak-time control plane deadlocks`) is merged into `main` as `dcda9d3890be390a90e9a967905f2cab3c6c7194`.

## Deployment truth

- Live controller/app is deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy passed: controller active, `/healthz` OK, configured repository ref exact, rollback backup `/var/backups/hermes-rdp/controller-20260812T095505Z`.
- Dedicated `hermes-rdp-sshd.service` was not restarted by the final deploy; PID remained unchanged, preserving active OpenSSH transport.
- MIPC agent live acceptance used immutable head `2a170b0f4961299227120afa2eb7c0fffb0f0d13`; subsequent PR #20 changes touched only server bot/registry/tests, not the Windows agent.

## Stabilization blockers — CLOSED

### CP-001 — TLS accept stall — COMPLETE PASS

Fix moves TLS handshake into the accepted connection worker and bounds handshake/client socket timeouts. Live bounded repro held a silent raw TCP client on `:7443` while five parallel `/healthz` requests all passed in 16–20 ms; controller and dedicated sshd PIDs remained unchanged and active telemetry stayed fresh.

Do not repeat the slow-handshake stress without a concrete regression reason.

### CL-001 — desired OFF + local ON deadlock — COMPLETE PASS

New Windows agent polls heartbeat/control before transport reconciliation and consumes durable `desired_enabled` independently of transient commands. Direct live acceptance on MIPC forced server desired OFF without queuing a new command (`command_seq` stayed 27). Agent remained online, converged applied access OFF, stopped SSH, closed endpoint within 5 seconds, then automatically recovered to ON/one SSH/open endpoint within 8 seconds after server desired state was restored.

Do not repeat this deadlock reproduction without a concrete regression reason.

### CU-001 — command pending forever — COMPLETE PASS

Existing OSIO seq 14 OFF timed out after the configured 60 seconds: pending state cleared, durable desired OFF stayed false, timeout result preserved the same seq/action, and endpoint remained closed. Late command-result after timeout is now rejected so it cannot overwrite the timeout result; regression coverage passed in CI #210.

## Telegram UI follow-up — COMPLETE PASS

- Dashboard now auto-renders when command/tunnel state changes; user confirmed OFF/ON state and buttons update without manual `🔄 ОБНОВИТЬ`.
- OFF and RESTART are separate full-width rows; user confirmed mobile Telegram renders both correctly.

## Stable accepted blocks

Do not repeat without a concrete regression reason:

- OpenSSH reverse RDP end-to-end and external-network RDP;
- Windows reboot recovery;
- Telegram OFF/ON and endpoint CLOSED/OPEN truth;
- MIPC performance/classification/Observe60 acceptance;
- Windows Server 2019 current-head acceptance;
- Win10 x64 + PowerShell x86/Sysnative acceptance;
- RL-001..RL-005 lifecycle recovery;
- RL-007 simultaneous multi-device user smoke;
- RL-008 one-device failure isolation;
- CP-001, CL-001 and CU-001 stabilization acceptance;
- Telegram UI auto-refresh/mobile button-layout acceptance.

## Stage 2 remaining work

### RL-006 repeated reconnect stress — PARTIAL PASS

Five consecutive dedicated-sshd restart cycles were clean server-side. Final Windows process-count check on the original tested machine was not collected. Do not repeat the five-cycle stress; if that exact machine is available later, one lightweight `HermesSshCount == 1` check is sufficient.

### RL-007 multi-device — COMPLETE PASS

Server-side evidence already showed four independent endpoints simultaneously healthy with successful TCP-through-tunnel checks. Final user-facing smoke also passed: two Microsoft RDP sessions to different Hermes devices were open and usable at the same time without mutual disruption.

### RL-008 failure isolation — COMPLETE PASS

A bounded live test held only MIPC (`:53389`) in durable desired OFF for 12 seconds without queueing a command. MIPC endpoint closed and its agent applied OFF/SSH count 0; other healthy devices kept fresh telemetry and open listeners throughout. Shared controller and dedicated sshd PIDs stayed unchanged, MIPC command sequence stayed unchanged, and MIPC automatically restored to ON/one SSH/open endpoint after desired state was restored. User confirmed the MIPC RDP session dropped as intended while the second active RDP session stayed continuously usable without interruption.

## Exact next action

Core Stage 2 lifecycle acceptance is complete except the deferred RL-006 single Windows process-count closure. Do not repeat the five-cycle stress. If the exact original RL-006 Windows machine is available, perform only one lightweight `HermesSshCount == 1` check; otherwise proceed to the next product stage: device/security lifecycle acceptance.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
