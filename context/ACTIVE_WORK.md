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

Server remains on immutable head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.

MIPC Windows agent is now on immutable head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.

This split is intentional: the diff from `586e944...` to `c51ed8fa...` changes only `client/HermesRdpAgent.ps1` and its static test; server code is unchanged.

Latest MIPC update proved:

- Scheduled Task = `Running`;
- `device_id`, assigned RDP port, `device.json` and private SSH key unchanged;
- exactly one Hermes `ssh.exe` immediately after update;
- `.NET` TCP fast path present;
- Hermes SSH PID cache present with 15-second rediscovery interval;
- loopback peer helper present;
- executable `Get-NetTCPConnection` call absent from the installed agent;
- local rollback copy created.

## Performance acceptance state

First runtime benchmark on `586e944...` showed the first telemetry split was incomplete:

```text
SSH filtered lookup   avg ~256 ms
RDP :3389 query       avg ~829 ms, max ~1347 ms
```

Those two operations were still too expensive for an ordinary 3-second path.

Second optimization on current head `c51ed8fa...` was then installed and measured live on MIPC:

```text
SSH cached PID        avg 21.63 ms, max 73.51 ms
.NET RDP snapshot     avg 19.68 ms, max 71.04 ms
FAST core combined    avg 27.46 ms, max 43.69 ms
SSH full refresh      avg 312.72 ms, max 401.56 ms
```

During this benchmark:

- one RDP connection was present;
- it was non-loopback/direct;
- loopback RDP count was zero;
- therefore native `netstat` peer correlation was not invoked.

Conclusion: **ordinary fast-path timing PASS**. The confirmed NetTCPIP/WMI bottleneck has been removed from the normal 3-second path.

Overall performance regression is **not yet fully closed** until:

1. subjective RDP smoothness is confirmed;
2. the 15-second background telemetry cadence is checked for noticeable periodic spikes;
3. Hermes loopback RDP exercises the conditional `netstat` peer path.

## Stable live baseline

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- raw Win10 x64 + x86 PowerShell `Sysnative` visibility/probe;
- earlier state/endpoint/RDP classification baseline.

Relevant behavior touched by the newest fast-path refactor remains under targeted revalidation.

## Windows Server

Confirmed old bug: installer rejected Windows Server through the client-only ProductType gate.

PR #19 allows ProductType 2/3 and has regression coverage.

Status: **IMPLEMENTED; REAL FRESH WINDOWS SERVER INSTALL PENDING**.

## Exact next engineering stage

1. confirm subjective RDP smoothness on the current MIPC agent;
2. check whether 15-second background telemetry causes a visible/measureable periodic spike;
3. targeted current-head smoke:
   - one Hermes `ssh.exe`;
   - OFF -> applied OFF + endpoint CLOSED;
   - ON -> one tunnel + endpoint OPEN;
   - direct LAN/VPN RDP -> Hermes=0/direct=1;
   - Hermes RDP -> Hermes=1/direct=0 and exercises loopback peer correlation;
   - endpoint open with no Hermes RDP client -> Hermes=0;
4. test `НАБЛЮДАТЬ 60с` + automatic stop;
5. real fresh Windows Server install;
6. fresh patched install from Win10 x64 + PowerShell x86;
7. reconcile PR #19 with current `main`, rerun CI/recheck mergeability;
8. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not terminal transcripts. See `SESSION_PROTOCOL.md` and `CONTEXT_LIFECYCLE.md`.