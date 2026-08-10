# Hermes RDP — Current State Snapshot

Updated: 2026-08-10

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Target release: **v1.2.0 — Stabilization**.
- **PR #19 is merged into `main`.**
- Reconciled PR head: `53f5b42c0a5d09f21a4df41c38a95ef533d0c6ec`.
- Merge commit: `3f81bde44208df40e1a2753dcadb8397211b9255`.
- Reconciled CI #175: **PASS** (Linux validation + Windows PowerShell 5.1 validation).

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

Durable boundaries:

- all Windows devices are equal clients;
- only Linux Hermes server is infrastructure-special;
- admin SSH remains independent;
- FRP is not active runtime transport;
- private per-device SSH key stays on Windows;
- server restricts public key to the assigned endpoint;
- Telegram is control plane, not RDP transport;
- agent heartbeat continues while RDP access is OFF.

## Deployment truth

- Linux server remains live on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Accepted Windows agents used product head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Repository reconciliation and merge did not change the already accepted product tree; current `main` contains the accepted PR product code plus current context.

## Stabilization acceptance — COMPLETE for PR #19 scope

### MIPC

- fast-path timing PASS;
- subjective Hermes RDP performance PASS;
- RV-001..RV-006 PASS;
- `НАБЛЮДАТЬ 60с` including automatic stop PASS.

### Windows Server

- Windows Server 2019 Datacenter ProductType=3 clean install PASS;
- current-head agent update preserving identity/key/port/config PASS;
- exactly one Hermes SSH process / fast-path markers PASS;
- real RDP through assigned endpoint PASS.

### Win10 x64 + PowerShell x86

- Windows 10 Pro 19045 x64 + PowerShell 5.1 x86 baseline PASS;
- Sysnative Microsoft OpenSSH resolver PASS;
- clean immutable current-head fresh install from x86 PowerShell PASS;
- canonical `C:\Windows\System32\OpenSSH\ssh.exe`, keys, `known_hosts`, Task=`Running`, one Hermes SSH process PASS;
- current fast path present / old executable NetTCPIP path absent PASS;
- real RDP through newly assigned endpoint PASS.

The Windows x86/WOW64/Sysnative compatibility bug is closed for the accepted product head.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- Windows reboot recovery;
- Telegram OFF/ON and endpoint CLOSED/OPEN truth;
- existing-install guard;
- MIPC current-head classification/control/performance acceptance;
- observation auto-stop;
- Windows Server full acceptance;
- Win10 x64 + PowerShell x86 full acceptance.

## Current stage — recovery / lifecycle matrix

Stage 2 is active after PR #19 merge.

Next acceptance order:

1. Telegram `RESTART` actually replaces the Hermes SSH transport and returns to exactly one tunnel while access stays ON;
2. temporary Windows network loss recovers automatically;
3. Linux server reboot recovers controller + dedicated sshd and clients reconnect;
4. controller restart recovery;
5. dedicated Hermes sshd restart recovery;
6. repeated reconnects create no duplicate/orphan Hermes SSH processes;
7. two+ devices work simultaneously;
8. failure of one device does not affect another.

Windows reboot is already PASS and is not repeated generically.
