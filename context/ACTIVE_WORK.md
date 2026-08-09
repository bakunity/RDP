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

The split is intentional: changes after `586e944...` are Windows-agent/test only, so no Linux redeploy was required.

## MIPC stabilization — COMPLETE

Current-head MIPC acceptance is green:

- ordinary fast-path timing **PASS**: cached SSH PID avg 21.63 ms, .NET RDP snapshot avg 19.68 ms, combined FAST core avg 27.46 ms / max 43.69 ms;
- subjective Hermes RDP smoothness **PASS**: no noticeable micro-freezes on the accepted working route;
- RV-001..RV-006 targeted smoke **PASS**;
- `НАБЛЮДАТЬ 60с` **PF-008 PASS**: countdown/live resource+TOP cadence worked and observation automatically returned to `Наблюдение выключено` after lease expiry without manual stop.

Do not repeat these checks without a concrete regression reason.

## Windows Server acceptance — ACTIVE STAGE

Real clean baseline/fresh install:

- Windows Server 2019 Datacenter;
- ProductType `3`;
- x64 OS + x64 PowerShell 5.1;
- no pre-existing Hermes directory/task;
- fresh immutable `586e944...` install reached `=== ГОТОВО ===`;
- old client-only ProductType rejection did not occur;
- OpenSSH tunnel/task were created and the user confirmed the newly added Server worked.

`scripts/install-client.ps1` is byte-identical at `586e944...` and current PR head `c51ed8...`, therefore the Windows Server installer/ProductType fix itself is **PASS**.

The Server agent has now been updated in place to immutable `c51ed8fa2c090dbc731a0c06f357d899846e90ae` with a local backup. Live post-update evidence:

- Scheduled Task = `Running`;
- device ID preserved;
- assigned RDP port preserved;
- config hash unchanged;
- private-key hash unchanged;
- exactly one Hermes `ssh.exe`;
- .NET TCP fast path present;
- SSH PID cache present with 15-second discovery interval;
- loopback peer helper present;
- executable old `Get-NetTCPConnection` RDP path absent.

This is **current-head agent update PASS**. One final Windows Server acceptance check remains: prove the assigned RDP endpoint is still usable after this `c51ed8...` update. Do not infer endpoint usability from process state alone.

Exact next action: connect to this Windows Server through its assigned Hermes RDP endpoint after the `c51ed8...` update and confirm the session opens. If yes, Windows Server current-head acceptance is complete.

## Stable live baseline

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- Win10 x64 + x86 PowerShell native `Sysnative` OpenSSH visibility/probe;
- MIPC fast-path/performance acceptance;
- RV-001..RV-006 current-head smoke;
- PF-008 observation-mode acceptance;
- Windows Server ProductType=3 fresh-installer acceptance;
- Windows Server `c51ed8...` in-place agent update preserving identity/key/port and one-SSH state.

## Remaining PR #19 acceptance

1. confirm the newly updated Windows Server endpoint is actually usable over RDP;
2. fresh patched Win10 x64 full install launched from PowerShell x86;
3. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
4. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, tokens, private keys or ready-to-use secret material in context.