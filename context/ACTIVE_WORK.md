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

The machine initially contained an older working Hermes installation created from normal x64 PowerShell. It was safely archived intact and its Scheduled Task exported, leaving no active Hermes directory/task for the fresh test.

### Fresh x86 install — INSTALLER PASS

Using the same elevated PowerShell x86 process and immutable current head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`, the fresh installer completed successfully to `=== ГОТОВО ===`:

- a new device registration was created;
- an RDP endpoint was assigned;
- transport reported `OpenSSH`;
- `Hermes RDP Agent` Scheduled Task was created;
- the installer did not fail on WOW64/System32 redirection.

This is the key live proof that the patched installer can complete from x86 PowerShell on x64 Win10. Full WI-003 acceptance is not complete yet: post-install state and real endpoint usability still need live confirmation.

Exact next action: inspect the newly installed config/task/process/agent state from the same x86 shell, confirming canonical `C:\Windows\System32\OpenSSH\ssh.exe`, key presence, Task=`Running`, exactly one Hermes SSH process, and current-head fast-path markers. Then perform one real RDP connection through the assigned endpoint.

The archived old `ai` installation remains rollback material. Do not restore it until the fresh x86 acceptance is complete or a rollback is intentionally chosen.

## Remaining PR #19 acceptance

1. finish Win10 x86 post-install smoke and real RDP endpoint test;
2. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
3. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.