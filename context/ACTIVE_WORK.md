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

This split is intentional: the diff after `586e944...` is Windows-agent/test only, so no Linux redeploy was required.

Current-head MIPC update preserved device ID, assigned RDP port, config and private key; Scheduled Task remained `Running`; the installed agent contains the .NET TCP fast path, 15-second Hermes SSH PID cache and loopback peer helper, with executable `Get-NetTCPConnection` removed from the RDP path.

## Performance acceptance

Live current-head timing on MIPC:

```text
SSH cached PID        avg 21.63 ms, max 73.51 ms
.NET RDP snapshot     avg 19.68 ms, max 71.04 ms
FAST core combined    avg 27.46 ms, max 43.69 ms
SSH full refresh      avg 312.72 ms, max 401.56 ms
```

Ordinary 3-second fast-path timing is **PASS**. The old NetTCPIP/WMI bottleneck is removed from normal per-cycle work.

Subjective Hermes RDP acceptance is also **PASS** on the restored working route: normal work is smooth, no noticeable micro-freezes, and no visible ~15-second periodic stall during the acceptance window. Direct LAN RDP remains somewhat more immediate, as expected.

## Current-head targeted smoke — COMPLETE

All current-head smoke obligations RV-001..RV-006 are now **PASS** on `c51ed8fa...`:

- **RV-001 PASS:** direct LAN/VPN RDP -> `Hermes=0/direct=1` while Hermes tunnel remains enabled.
- **RV-002 PASS:** active Hermes RDP -> `Hermes=1/direct=0`; current loopback peer-correlation path is live-proven.
- **RV-003 PASS:** Hermes endpoint/tunnel open with no RDP client -> `Hermes=0/direct=0`.
- **RV-004 PASS:** Telegram OFF/ON command delivery and applied-state transition work on current head.
- **RV-005 PASS:** normal ON state has exactly one Hermes `ssh.exe`; latest live check returned one PID and Scheduled Task `Running`.
- **RV-006 PASS:** OFF -> endpoint CLOSED / SSH disconnected; ON -> endpoint OPEN / SSH connected.

Do not repeat RV-001..RV-006 without a concrete regression reason.

## Observation-mode acceptance — ACTIVE STAGE

`НАБЛЮДАТЬ 60с` has now been started on MIPC and live activation is confirmed:

- dashboard reports observation enabled with a remaining-seconds countdown;
- resource age is ~3 seconds during observation;
- TOP-process data is populated and refreshed (observed snapshot age 7 seconds with five processes);
- ordinary access/tunnel state remains healthy during observation.

This is **activation/cadence PARTIAL PASS**, not final PF-008 acceptance yet.

Exact next check: after the 60-second lease expires, refresh the MIPC card and confirm observation automatically returns to `Наблюдение выключено` without manually stopping it. If yes, PF-008 becomes PASS and observation-mode acceptance is complete.

## Stable live baseline

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- raw Win10 x64 + x86 PowerShell `Sysnative` visibility/probe;
- current-head RV-001..RV-006 targeted smoke;
- current-head ordinary fast-path timing and subjective smoothness on the accepted working Hermes path.

## Windows Server

Confirmed old bug: installer rejected Windows Server through the client-only ProductType gate.

PR #19 allows ProductType 2/3 and has regression coverage.

Status: **IMPLEMENTED; REAL FRESH WINDOWS SERVER INSTALL PENDING**.

## Next stages after observation acceptance

1. real fresh Windows Server install;
2. fresh patched Win10 x64 full install launched from PowerShell x86;
3. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
4. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. See `SESSION_PROTOCOL.md` and `CONTEXT_LIFECYCLE.md`.