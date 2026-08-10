# Hermes RDP — Active Work

Updated: 2026-08-10

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- Current PR head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- Product code from PR #19 is still unmerged.

## Deployment truth

Server remains on immutable head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.

MIPC Windows agent is on immutable head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.

The accepted Windows Server 2019 Datacenter device is also running immutable `c51ed8...` and has a live-proven Hermes RDP endpoint.

## Accepted stabilization blocks

### MIPC — COMPLETE

- ordinary fast-path timing **PASS**;
- subjective Hermes RDP smoothness **PASS**;
- RV-001..RV-006 targeted smoke **PASS**;
- `НАБЛЮДАТЬ 60с` / PF-008 including automatic stop **PASS**.

### Windows Server — COMPLETE

Real clean Windows Server 2019 Datacenter acceptance is fully green:

- ProductType `3`, x64, PowerShell 5.1, no pre-existing Hermes dir/task;
- fresh installer reached `=== ГОТОВО ===` and old client-only rejection did not occur;
- installer/ProductType fix is live-proven;
- agent updated to immutable `c51ed8...` preserving identity/key/port/config;
- Scheduled Task=`Running`;
- exactly one Hermes `ssh.exe`;
- current fast-path markers present and old executable `Get-NetTCPConnection` RDP path absent;
- real RDP connection through the assigned Hermes endpoint succeeded after the current-head update.

Do not repeat MIPC or Windows Server acceptance without a concrete regression reason.

## Current stage — Win10 x64 + PowerShell x86 fresh install

The real target machine is Windows 10 Pro build 19045 with x64 OS and 32-bit PowerShell 5.1 under `SysWOW64`.

Runtime compatibility baseline is **PASS**:

- `OS64Bit=True`;
- `Process64Bit=False`;
- process path is `SysWOW64\WindowsPowerShell\v1.0\powershell.exe`;
- OpenSSH capability is installed;
- `Sysnative\OpenSSH\ssh.exe` and `ssh-keygen.exe` are visible;
- native Microsoft OpenSSH executes successfully through `Sysnative`.

The machine initially contained an older working Hermes installation created from normal x64 PowerShell. It was not overwritten. That installation was safely stopped, its Scheduled Task exported, and the entire local Hermes directory moved aside intact. Server registration was not deleted.

Fresh-test baseline is now **PASS**:

- `C:\ProgramData\HermesRDP` absent;
- `Hermes RDP Agent` Scheduled Task absent;
- archived prior installation exists for rollback;
- current shell remains 32-bit PowerShell on x64 Windows.

Exact next action: generate a fresh pair code in Telegram, then run the immutable current-head installer from this same elevated PowerShell x86 process with `RepositoryRef=c51ed8fa2c090dbc731a0c06f357d899846e90ae`. After install, verify canonical System32 SSH path, task/tunnel/endpoint and real RDP connectivity. Do not restore the archived old installation unless the test fails or acceptance is complete and rollback is intentionally chosen.

## Remaining PR #19 acceptance

1. complete the fresh patched Win10 x64 install from PowerShell x86 and real endpoint test;
2. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
3. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.