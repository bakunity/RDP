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

A newly added Windows Server 2019 Datacenter device was fresh-installed successfully using immutable ref `586e944...`. It currently runs the `586e944...` agent because that ref was passed as `RepositoryRef`. The installer script itself is byte-identical at `586e944...` and current PR head `c51ed8...`, so the ProductType fix is directly validated; only an agent-only update/smoke remains to put this Server on the newest current-head agent.

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

Real clean acceptance now proves:

- Windows Server 2019 Datacenter, ProductType=3, x64, PowerShell 5.1;
- no pre-existing Hermes directory/task;
- fresh installer completed to `=== ГОТОВО ===`;
- OpenSSH tunnel/task created and persistent endpoint assigned;
- user confirmed the added Server works;
- old client-only rejection is gone.

Status:

- Windows Server installer/ProductType fix — **PASS**;
- newest `c51ed8...` agent on that Server — **REVALIDATION REQUIRED** only because the successful fresh install used `RepositoryRef=586e944...`.

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
- Win10 x64/x86 PowerShell Sysnative OpenSSH probe behavior.

## CI / PR state

Current PR head `c51ed8fa...` has green CI #139 from before the latest context-only `main` commits. PR remains open and must be reconciled with advanced `main`, then CI/mergeability rechecked before merge.

## Immediate blockers before PR #19 merge

1. update the new Windows Server agent to immutable `c51ed8...` and smoke task/one-SSH/endpoint while preserving identity/key/port;
2. fresh Win10 x64 full install launched from PowerShell x86;
3. reconcile feature branch with current `main`, rerun CI and recheck mergeability;
4. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.