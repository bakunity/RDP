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

The newly added Windows Server 2019 Datacenter device is also running the immutable `c51ed8...` agent after an in-place update that preserved device ID, assigned RDP port, config and private key.

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
- .NET TCP fast path, 15-second SSH PID cache and loopback peer helper present;
- old executable `Get-NetTCPConnection` RDP path absent;
- real RDP connection through the assigned Hermes endpoint succeeded after the current-head update.

Do not repeat MIPC or Windows Server acceptance without a concrete regression reason.

## Current stage — Win10 x64 + PowerShell x86 fresh install

Raw runtime behavior is already proven: on x64 Windows launched under 32-bit PowerShell, `Sysnative` reaches native Microsoft OpenSSH and the resolver avoids PATH/Git SSH fallback.

What remains is one real end-to-end fresh install on a clean Win10 x64 machine launched specifically from PowerShell x86.

Acceptance target:

- clean Hermes state before install;
- 64-bit OS + 32-bit PowerShell process confirmed;
- patched installer used from immutable current code;
- native Microsoft OpenSSH selected through Sysnative/canonical System32 handling;
- key/task/tunnel/endpoint complete successfully;
- real RDP connection through the assigned endpoint works.

Exact next action: collect the Win10 pre-install baseline only. Do not run the installer until the baseline is reviewed.

## Remaining PR #19 acceptance

1. fresh patched Win10 x64 full install launched from PowerShell x86;
2. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
3. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.