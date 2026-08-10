# Hermes RDP — Current State Snapshot

Updated: 2026-08-10

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Active stabilization PR: **#19**, branch `fix/control-state-dashboard`.
- Current PR head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Target release: **v1.2.0 — Stabilization**.
- Product changes from PR #19 are not merged to `main` yet.
- Context-only commits continue to advance `main`; feature branch must be reconciled with current base + CI before merge.

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

Server is live on immutable head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.

MIPC Windows agent is live on immutable head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.

The accepted Windows Server 2019 Datacenter device also runs immutable `c51ed8...`; its identity/key/port/config survived update and its real Hermes RDP endpoint works after the update.

## Stabilization acceptance — accepted blocks

### MIPC

Accepted on `c51ed8...`:

- fast-path timing PASS;
- subjective smooth Hermes RDP PASS;
- RV-001..RV-006 targeted classification/control/process smoke PASS;
- `НАБЛЮДАТЬ 60с` PF-008 PASS, including automatic stop after lease expiry.

Performance regression status: **RESOLVED FOR THE CURRENT TESTED WORKING PATH**.

### Windows Server

Real clean acceptance is **COMPLETE PASS**:

- Windows Server 2019 Datacenter, ProductType=3, x64, PowerShell 5.1;
- no pre-existing Hermes directory/task before fresh install;
- fresh installer completed to `=== ГОТОВО ===`;
- old client-only rejection is gone;
- current-head agent update to `c51ed8...` preserved identity/key/port/config;
- Task=`Running` and exactly one Hermes `ssh.exe` after update;
- expected current-head fast-path implementation installed;
- real RDP session through the assigned Hermes endpoint succeeded after the update.

Do not repeat these accepted blocks without a concrete regression reason.

## Windows compatibility — current stage

### Win10 x64 + x86 PowerShell

Real target machine:

- Windows 10 Pro build 19045;
- x64 OS;
- PowerShell 5.1 running as 32-bit process from `SysWOW64`;
- Microsoft OpenSSH capability installed;
- native `ssh.exe` and `ssh-keygen.exe` visible through `Sysnative`;
- native OpenSSH execution through `Sysnative` confirmed.

The machine originally had an older Hermes client installed from normal x64 PowerShell. For a genuine fresh x86 acceptance test, that local installation was safely archived intact and its Scheduled Task exported; server registration was not deleted.

Fresh-test baseline was confirmed with active Hermes directory/task absent while the shell remained x86.

The immutable current-head installer `c51ed8...` has now been run from that same x86 PowerShell process and reached `=== ГОТОВО ===`. It created a new device registration, assigned a public RDP endpoint, created `Hermes RDP Agent`, and reported OpenSSH transport. This directly proves the installer no longer fails because the launching process is 32-bit on x64 Win10.

Status:

- Sysnative runtime/probe — **PASS**;
- clean x86 fresh-test baseline — **PASS**;
- immutable current-head installer completion from x86 PowerShell — **PASS**;
- post-install canonical System32 SSH/key/task/one-SSH/current-agent verification — **PENDING**;
- real RDP through the newly assigned endpoint — **PENDING**.

The archived original `ai` local installation remains available for rollback and has not been restored.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- Telegram OFF/ON and endpoint CLOSED/OPEN truth;
- existing-install guard;
- current-head MIPC RV-001..RV-006;
- MIPC fast-path/performance acceptance;
- PF-008 observation auto-stop;
- complete Windows Server ProductType/current-head/end-to-end acceptance;
- Win10 x64/x86 PowerShell Sysnative OpenSSH runtime behavior;
- Win10 immutable current-head fresh installer completion from x86 PowerShell.

## CI / PR state

Current PR head `c51ed8fa...` has green CI #139 from before the latest context-only `main` commits. PR remains open and must be reconciled with advanced `main`, then CI/mergeability rechecked before merge.

## Immediate blockers before PR #19 merge

1. finish Win10 x86 post-install smoke and real endpoint test;
2. reconcile feature branch with current `main`, rerun CI and recheck mergeability;
3. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.