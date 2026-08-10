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
- OpenSSH reverse RDP end-to-end, external-network RDP, Windows reboot recovery, Telegram OFF/ON and endpoint CLOSED/OPEN truth.

## Deployment truth

- Linux server remains on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Merge/reconciliation changed repository history/context, not the already accepted product behavior.

## Current stage — recovery / lifecycle matrix

PR #19 merge gate is complete. Stage 2 is now active.

Order:

1. **RESTART command** must actually stop the current Hermes SSH transport and recreate a fresh single tunnel while keeping access enabled.
2. Temporary Windows network loss -> automatic reconnect.
3. Linux server reboot -> controller + dedicated sshd recover -> clients reconnect.
4. Controller restart -> clients recover.
5. Dedicated Hermes sshd restart -> clients recover.
6. Repeated reconnects -> no duplicate/orphan Hermes SSH processes.
7. Two+ devices simultaneously.
8. One device failure must not affect another.

Windows reboot recovery is already PASS and is not repeated as a generic test.

## Exact next action

Inspect and live-test the Telegram **RESTART** path on one accepted current-head Windows device. Source contract on merged `main` is:

`restart` -> agent sets access enabled -> `Restart-SshTunnel` -> force-discover/stop Hermes SSH -> wait 1 second -> start one new SSH tunnel -> report command result.

Acceptance requires proof that the SSH PID changes, process count returns to exactly 1, desired/applied access remains ON, endpoint returns OPEN, and a real RDP connection still works after RESTART.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.
