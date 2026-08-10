# Hermes RDP — Active Work

Updated: 2026-08-10

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- Accepted product head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- Product code from PR #19 is still unmerged.

## Deployment truth

- Linux server remains on immutable head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- MIPC Windows agent runs immutable `c51ed8...`.
- Accepted Windows Server 2019 device runs immutable `c51ed8...` and its real Hermes endpoint works.
- Win10 Pro 19045 x64 fresh x86-PowerShell acceptance device runs immutable `c51ed8...` and its real Hermes endpoint works.

## Completed live acceptance for PR #19

### MIPC — COMPLETE

- ordinary fast-path timing **PASS**;
- subjective Hermes RDP smoothness **PASS**;
- RV-001..RV-006 targeted smoke **PASS**;
- `НАБЛЮДАТЬ 60с` including automatic stop **PASS**.

### Windows Server — COMPLETE

- clean Windows Server 2019 Datacenter ProductType=3 install **PASS**;
- current-head agent update preserving identity/key/port/config **PASS**;
- Task=`Running`, exactly one Hermes `ssh.exe`, current fast-path markers **PASS**;
- real RDP through assigned endpoint **PASS**.

### Win10 x64 + PowerShell x86 — COMPLETE

Real target: Windows 10 Pro build 19045, x64 OS, PowerShell 5.1 as a 32-bit `SysWOW64` process.

Live proof on immutable `c51ed8...`:

- `Sysnative\OpenSSH\ssh.exe` and `ssh-keygen.exe` visible and native Microsoft OpenSSH executes;
- previous local Hermes install archived intact; active Hermes directory/task absent before fresh test;
- fresh installer launched from the same elevated x86 PowerShell reached `=== ГОТОВО ===`;
- config stores canonical `C:\Windows\System32\OpenSSH\ssh.exe`;
- private/public key and `known_hosts` exist;
- Scheduled Task=`Running`;
- exactly one Hermes SSH process;
- current `.NET` RDP fast path, 15-second SSH PID cache and loopback peer helper present;
- old executable `Get-NetTCPConnection` RDP path absent;
- real RDP connection through the newly assigned public endpoint succeeded.

**WI-003 COMPLETE PASS.** The Win10 x64 + PowerShell x86 / WOW64 / Sysnative compatibility bug is closed for the tested current product head.

Do not repeat completed Windows/MIPC live acceptance without a concrete regression reason.

## Current stage — PR #19 merge preparation

Live runtime acceptance is green. The only active gate is repository reconciliation.

Current known branch state before reconciliation:

- PR #19 head: `c51ed8fa...`;
- `main` advanced through context-only commits after the feature branch split;
- comparison shows product branch and `main` diverged from merge base `6cecc33d...`;
- `main`-only changes are under `context/`;
- GitHub currently reports PR mergeable, but CI must be rerun after explicit reconciliation.

Exact next action:

1. reconcile current `main` into `fix/control-state-dashboard` without changing accepted product code;
2. verify resulting diff still contains only intended PR product changes plus current context;
3. wait for/rerun CI on reconciled head;
4. recheck mergeability;
5. merge PR #19 only if the reconciled gate is green.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.
