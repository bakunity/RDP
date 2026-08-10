# Hermes RDP — Active Work

Updated: 2026-08-10

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- **PR #19 is MERGED.**
- Reconciled PR head: `53f5b42c0a5d09f21a4df41c38a95ef533d0c6ec`.
- Merge commit now on `main`: `3f81bde44208df40e1a2753dcadb8397211b9255`.
- CI #175 on the reconciled PR head: **PASS** for Linux validation and Windows PowerShell 5.1 validation.

## Accepted stabilization blocks

Do not repeat without a concrete regression reason:

- MIPC fast-path timing and subjective performance;
- RV-001..RV-006 classification/control/process smoke;
- `НАБЛЮДАТЬ 60с` including automatic stop;
- Windows Server 2019 ProductType=3 fresh-install/current-head/RDP acceptance;
- Win10 Pro 19045 x64 + 32-bit PowerShell fresh-install/Sysnative/current-head/RDP acceptance;
- existing-install duplicate Add guard;
- OpenSSH reverse RDP end-to-end, external-network RDP, Windows reboot recovery, Telegram OFF/ON and endpoint CLOSED/OPEN truth;
- Stage 2 RL-001 Telegram RESTART end-to-end recovery;
- Stage 2 RL-002 automatic Hermes transport recovery after temporary Windows-side network loss;
- Stage 2 RL-003 Linux server reboot recovery;
- Stage 2 RL-004 controller restart isolation.

## Deployment truth

- Linux server remains on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Merge/reconciliation changed repository history/context, not the already accepted product behavior.

## Current stage — recovery / lifecycle matrix

PR #19 merge gate is complete. Stage 2 is active.

### RL-001 Telegram RESTART — COMPLETE PASS

Live-tested on the accepted Win10 x64/x86-PowerShell device. RESTART replaced the old Hermes SSH PID with a different PID, returned to exactly one SSH process, kept access ON, returned endpoint OPEN, and the already-open RDP session automatically recovered after the short transport interruption.

### RL-002 Temporary Windows-side network loss — COMPLETE PASS

A reversible transport-scoped firewall block killed the old Hermes SSH process. After removing the block, the existing agent automatically created one new SSH process with access still enabled and without Telegram ON/RESTART. RDP through the endpoint worked again. The intentionally long outage exceeded the Microsoft RDP client's reconnect window; that client behavior is not treated as Hermes recovery failure.

### RL-003 Linux server reboot — COMPLETE PASS

A real `systemctl reboot` was performed after a healthy baseline. The server returned, Telegram/dashboard recovered, Windows reverse transport returned without manual recovery action, and the already-open RDP session automatically restored.

### RL-004 Controller restart isolation — COMPLETE PASS

Live controller-only restart on the Linux server proved architectural separation:

- `hermes-rdp.service` controller PID changed and returned `active`;
- `hermes-rdp-sshd.service` PID stayed unchanged and remained `active`;
- existing `sshd-session` PID for the tested endpoint stayed unchanged;
- listeners on dedicated SSH `:7000` and the tested public RDP endpoint remained present;
- Telegram/dashboard continued working after controller restart;
- the active RDP session had no interruption or visible reconnect.

This proves controller lifecycle is isolated from the dedicated OpenSSH transport on the tested deployment.

Do not repeat RL-001..RL-004 without a concrete regression reason.

## Remaining Stage 2 order

1. **Dedicated Hermes sshd restart -> clients recover.**
2. Repeated reconnects -> no duplicate/orphan Hermes SSH processes.
3. Two+ devices simultaneously.
4. One device failure must not affect another.

Windows reboot recovery is already PASS and is not repeated as a generic test.

## Exact next action

Run RL-005 by restarting only `hermes-rdp-sshd.service` while leaving `hermes-rdp.service` untouched. Keep the active Hermes RDP session open. Acceptance: controller PID remains unchanged/active; dedicated sshd PID changes and returns active; old endpoint `sshd-session` is replaced; the Windows agent reconnects automatically without Telegram ON/RESTART; exactly one endpoint listener returns; Telegram/dashboard remains healthy; and the active RDP client either automatically resumes or any interruption is recorded explicitly.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.
