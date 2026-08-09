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

A newly added Windows Server 2019 Datacenter device was first fresh-installed successfully using immutable ref `586e944...`. The installer script is byte-identical at `586e944...` and current PR head `c51ed8...`, so the Windows Server ProductType fix is directly live-validated.

That Windows Server agent has now been updated in place to immutable `c51ed8...`. The update preserved device ID, assigned RDP port, config and private key; Scheduled Task is Running; exactly one Hermes `ssh.exe` is present; current-head .NET TCP/SSH-cache/loopback-peer markers are present and the old executable `Get-NetTCPConnection` RDP path is absent.

One boundary remains: the assigned public RDP endpoint must still be proved usable after the current-head agent update.

## Stabilization acceptance — current

The MIPC stabilization block is accepted on `c51ed8...`:

- fast-path timing PASS;
- subjective smooth Hermes RDP PASS;
- RV-001..RV-006 targeted classification/control/process smoke PASS;
- `НАБЛЮДАТЬ 60с` PF-008 PASS, including automatic stop after lease expiry.

Performance regression status: **RESOLVED FOR THE CURRENT TESTED WORKING PATH**.

## Windows compatibility

### Win10 x64 + x86 PowerShell

Confirmed runtime behavior:

- 64-bit Windows under 32-bit PowerShell experiences WOW64 redirection;
- `Sysnative` reaches native Microsoft OpenSSH;
- installer resolver stores canonical `System32` path and avoids PATH/Git SSH fallback.

Status:

- raw Sysnative visibility/probe — **PASS**;
- existing-install guard — **PASS**;
- genuinely fresh full patched install launched from x86 PowerShell — **IMPLEMENTED, NOT VALIDATED**.

### Windows Server

Old bug: installer rejected `ProductType != 1` before its later Server edition check.

Current implementation accepts ProductType 2/3 for recognized Windows Server editions.

Live acceptance now proves:

- Windows Server 2019 Datacenter, ProductType=3, x64, PowerShell 5.1;
- no pre-existing Hermes directory/task before fresh install;
- fresh installer completed to `=== ГОТОВО ===`;
- old client-only rejection is gone;
- current-head agent update to `c51ed8...` preserved identity/key/port/config;
- Task=`Running` and one Hermes `ssh.exe` after update;
- expected current-head fast-path implementation is installed.

Status:

- Windows Server installer/ProductType fix — **PASS**;
- Windows Server current-head agent update — **PASS**;
- post-update assigned RDP endpoint usability — **PENDING FINAL LIVE CONFIRMATION**.

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
- Windows Server ProductType=3 fresh installer acceptance;
- Windows Server current-head agent update preserving identity/key/port and one-SSH state;
- Win10 x64/x86 PowerShell Sysnative OpenSSH probe behavior.

## CI / PR state

Current PR head `c51ed8fa...` has green CI #139 from before the latest context-only `main` commits. PR remains open and must be reconciled with advanced `main`, then CI/mergeability rechecked before merge.

## Immediate blockers before PR #19 merge

1. prove the newly updated Windows Server endpoint remains usable over RDP;
2. fresh Win10 x64 full install launched from PowerShell x86;
3. reconcile feature branch with current `main`, rerun CI and recheck mergeability;
4. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.