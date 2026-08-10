# Hermes RDP — Current State Snapshot

Updated: 2026-08-10

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Active stabilization PR: **#19**, branch `fix/control-state-dashboard`.
- Accepted product head before reconciliation: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Target release: **v1.2.0 — Stabilization**.
- Product changes from PR #19 are not merged to `main` yet.

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

- Linux server is live on immutable `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- MIPC Windows agent is live on immutable `c51ed8fa...`.
- Accepted Windows Server 2019 device runs immutable `c51ed8...` and its real endpoint works.
- Win10 Pro 19045 x64 fresh x86-PowerShell acceptance device runs immutable `c51ed8...` and its real endpoint works.

## Stabilization acceptance — COMPLETE for current product head

### MIPC

Accepted on `c51ed8...`:

- fast-path timing PASS;
- subjective smooth Hermes RDP PASS;
- RV-001..RV-006 targeted classification/control/process smoke PASS;
- `НАБЛЮДАТЬ 60с` including automatic stop PASS.

Performance regression status: **RESOLVED FOR THE CURRENT TESTED WORKING PATH**.

### Windows Server

Real clean acceptance is **COMPLETE PASS**:

- Windows Server 2019 Datacenter, ProductType=3, x64, PowerShell 5.1;
- fresh installer completed to `=== ГОТОВО ===`;
- old client-only rejection is gone;
- current-head agent update preserved identity/key/port/config;
- Task=`Running`, exactly one Hermes `ssh.exe`, expected current-head fast-path implementation;
- real RDP through assigned endpoint succeeded.

### Win10 x64 + PowerShell x86

Real acceptance is **COMPLETE PASS**:

- Windows 10 Pro build 19045, x64 OS;
- PowerShell 5.1 launched as a 32-bit `SysWOW64` process;
- native Microsoft OpenSSH visible/executable through `Sysnative`;
- previous local Hermes installation archived intact before clean fresh test;
- immutable `c51ed8...` installer reached `=== ГОТОВО ===` from the same x86 shell;
- config stores canonical `C:\Windows\System32\OpenSSH\ssh.exe`;
- key/public key/`known_hosts` exist;
- Task=`Running`, exactly one Hermes SSH process;
- current `.NET` fast path, SSH PID cache and loopback peer helper present;
- old executable `Get-NetTCPConnection` RDP path absent;
- real RDP through newly assigned endpoint succeeded.

The Windows x86/WOW64/Sysnative compatibility bug is therefore closed for the accepted product head.

Do not repeat accepted MIPC/Windows runtime blocks without a concrete regression reason.

## Repository / PR state

Live runtime acceptance is complete. Remaining work is repository-only merge preparation.

Before reconciliation:

- PR #19 head is `c51ed8fa...`;
- merge base with current `main` is `6cecc33d...`;
- `main` advanced after branch split through context-only commits;
- comparison from feature head to current `main` shows the `main`-only delta under `context/`;
- GitHub currently reports PR mergeable, but this is not the final gate because CI must run on the reconciled head.

## Immediate blockers before PR #19 merge

1. reconcile `fix/control-state-dashboard` with current `main` while preserving accepted product code;
2. verify reconciled diff/provenance;
3. rerun CI on the reconciled head;
4. recheck mergeability;
5. merge only when the reconciled gate is green.
