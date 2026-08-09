# Hermes RDP — Active Work

Updated: 2026-08-09

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- Current PR head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- Product code from PR #19 is still unmerged.

## Deployment truth

Server and MIPC currently run immutable head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.

Accepted deployment facts:

- both Hermes server services active after immutable updater run;
- server rollback backup created;
- MIPC Scheduled Task Running;
- `device_id`, assigned port, `device.json` and private SSH key unchanged;
- exactly one Hermes `ssh.exe` immediately after update;
- local Windows rollback copy created.

New PR head `c51ed8fa...` changes only `client/HermesRdpAgent.ps1` + its static test relative to deployed `586e944...`; server code is unchanged, so no Linux redeploy is required for the next performance acceptance.

## Performance acceptance state

First runtime benchmark on deployed low-cost head `586e944...` showed the telemetry split helped, but the fast path remained too expensive:

```text
SSH filtered lookup   avg ~256 ms
RDP :3389 query       avg ~829 ms, max ~1347 ms
CPU telemetry         avg ~358 ms   (15s/background)
OS + RAM              avg ~289 ms   (15s/background)
Disk                   avg ~35 ms   (15s/background)
Network                avg ~271 ms  (15s/background; noisy max)
```

Conclusion: **performance fix is not yet PASS**. The remaining fast-path bottlenecks were the NetTCPIP RDP query and repeated WMI SSH lookup.

Current PR head `c51ed8fa...` implements a second optimization:

- normal RDP discovery uses in-process `.NET IPGlobalProperties.GetActiveTcpConnections()` instead of `Get-NetTCPConnection`;
- native `netstat -ano -p tcp` is used only when an actual loopback RDP connection needs peer-PID correlation;
- Hermes SSH PIDs are cached;
- normal 3-second SSH checks use cheap `Get-Process -Id`;
- full `Win32_Process` discovery is moved out of the ordinary fast path and refreshed periodically / after cache loss;
- PowerShell 5.1 parse and full CI #139 are PASS.

Status: **IMPLEMENTED + CI PASS; MIPC LIVE UPDATE/BENCHMARK PENDING**.

## Stable live baseline

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- raw Win10 x64 + x86 PowerShell `Sysnative` visibility/probe;
- earlier state/endpoint/RDP classification baseline.

Relevant behavior touched by the latest fast-path refactor remains under targeted revalidation.

## Windows Server

Confirmed old bug: installer rejected Windows Server through the client-only ProductType gate.

PR #19 allows ProductType 2/3 and has regression coverage.

Status: **IMPLEMENTED; REAL FRESH WINDOWS SERVER INSTALL PENDING**.

## Exact next engineering stage

1. update MIPC agent only to immutable head `c51ed8fa2c090dbc731a0c06f357d899846e90ae` with rollback while preserving identity/key/port;
2. benchmark `.NET TCP snapshot`, cached SSH PID path, and subjective RDP smoothness;
3. if performance materially improves, run targeted current-head smoke:
   - one Hermes `ssh.exe`;
   - OFF -> applied OFF + endpoint CLOSED;
   - ON -> one tunnel + endpoint OPEN;
   - direct LAN/VPN RDP -> Hermes=0/direct=1;
   - Hermes RDP -> Hermes=1/direct=0;
   - endpoint open with no Hermes RDP client -> Hermes=0;
4. test `НАБЛЮДАТЬ 60с` + automatic stop;
5. real fresh Windows Server install;
6. fresh patched install from Win10 x64 + PowerShell x86;
7. reconcile PR #19 with current `main`, rerun CI/recheck mergeability;
8. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not terminal transcripts. See `SESSION_PROTOCOL.md` and `CONTEXT_LIFECYCLE.md`.