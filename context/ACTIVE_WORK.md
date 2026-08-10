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
- Stage 2 RL-003 Linux server reboot recovery.

## Deployment truth

- Linux server remains on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Merge/reconciliation changed repository history/context, not the already accepted product behavior.

## Current stage — recovery / lifecycle matrix

PR #19 merge gate is complete. Stage 2 is active.

### RL-001 Telegram RESTART — COMPLETE PASS

Live-tested on the accepted Win10 x64/x86-PowerShell device:

- before RESTART: access enabled, Task=`Running`, exactly one Hermes SSH PID;
- Telegram RESTART advanced command sequence and killed the old Hermes SSH process;
- a new different SSH PID appeared;
- exactly one Hermes SSH process remained;
- desired/applied access stayed ON;
- agent stayed ONLINE;
- SSH tunnel returned CONNECTED and public endpoint returned OPEN;
- active RDP through Hermes briefly reported connection loss during transport replacement, then recovered automatically without the user leaving/recreating the RDP session;
- dashboard returned `Hermes=1/direct=0` and last command `перезапуск туннеля` successful.

### RL-002 Temporary Windows-side network loss — COMPLETE PASS

A reversible outbound firewall block was applied only to the Hermes OpenSSH transport. Live evidence:

- old Hermes SSH PID exited during the block;
- after the block was removed, the existing agent recreated one new SSH process automatically;
- recovered PID differed from the old PID;
- exactly one Hermes SSH process remained;
- access remained enabled and Scheduled Task remained Running;
- command sequence did not change, proving no Telegram ON/RESTART was used;
- temporary firewall rule was removed successfully;
- RDP through the endpoint worked normally again after recovery.

RDP continuity interpretation: the test intentionally held the transport down long enough that Microsoft RDP exhausted its finite reconnect attempts (user observed roughly five retry cycles) and stopped retrying. Manual reconnection afterward succeeded immediately. This is not treated as a Hermes recovery defect. RL-001 already proves that a shorter transport interruption can be survived by the already-open RDP session automatically.

### RL-003 Linux server reboot — COMPLETE PASS

Before reboot the live server had both `hermes-rdp.service` and `hermes-rdp-sshd.service` enabled and active, dedicated SSH listener `:7000` open, and the tested device endpoint listener open. A real `systemctl reboot` was then performed. After the machine returned, the user confirmed:

- the server came back normally;
- Telegram control and dashboard worked again;
- the Windows client/tunnel recovered without reported manual recovery action;
- the already-open RDP session automatically restored and was usable again.

This proves the full server reboot path restores controller, dedicated sshd, reverse tunnel and live RDP service on the tested deployment.

Do not repeat RL-001..RL-003 without a concrete regression reason.

## Remaining Stage 2 order

1. **Controller restart -> clients recover / transport remains healthy.**
2. Dedicated Hermes sshd restart -> clients recover.
3. Repeated reconnects -> no duplicate/orphan Hermes SSH processes.
4. Two+ devices simultaneously.
5. One device failure must not affect another.

Windows reboot recovery is already PASS and is not repeated as a generic test.

## Exact next action

Run RL-004 by restarting only `hermes-rdp.service` while leaving `hermes-rdp-sshd.service` untouched. Keep an active Hermes RDP session open. Acceptance: controller PID changes and returns active, dedicated sshd remains active, the reverse-tunnel endpoint remains available, Telegram/dashboard returns, and the existing RDP transport stays usable without Windows-side ON/RESTART. If the active RDP session is interrupted, record that separately rather than hiding it.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.
