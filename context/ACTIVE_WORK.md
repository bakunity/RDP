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

During this benchmark one non-loopback/direct RDP connection was present, so conditional native `netstat` peer correlation was not invoked by that benchmark.

Conclusion: **ordinary fast-path timing PASS**. The confirmed NetTCPIP/WMI bottleneck has been removed from the normal 3-second path.

### Subjective runtime acceptance

After the second optimization and route experiments, the current working Hermes RDP session was used normally for an extended short acceptance window. User reported:

- work is comfortable;
- no noticeable lag/micro-freezes;
- motion/interaction is smooth;
- Hermes RDP is clearly better than before the optimization;
- direct RDP inside the local network still feels somewhat more immediate, as expected, but Hermes RDP is now considered good for normal work.

No noticeable ~15-second periodic stall was reported during this acceptance window.

Conclusion: **subjective RDP performance PASS for the current working Hermes path**. The original user-visible micro-freeze regression is considered resolved for this scenario.

### Network latency diagnosis

External client -> public Hermes host:

```text
ICMP loss 0%
RTT min 86 ms
RTT avg 101 ms
RTT max 129 ms
```

MIPC initially appeared to reach the public Hermes host in `0–3 ms` by ICMP and `1.5–9 ms` by TCP connect. Routing inspection proved those values were local TUN/proxy acceptance timings: the destination was intercepted by `Karing TUN Network Adapter`, and `tracert` reported the public host as one-hop `<1 ms`.

A remote SSH-banner measurement through Karing then returned:

```text
min 783.2 ms
avg 804.7 ms
max 870.9 ms
```

This is **not RTT**; it includes new TCP/proxy setup plus waiting for the real remote SSH banner. It proves that new remote-response setup through the Karing path is expensive, but does not by itself measure steady-state RDP latency.

A client-side RDP negotiation probe through the already-established Hermes tunnel then measured:

```text
TCP connect median ~92 ms (one 1092.7 ms outlier)
RDP response min 302.7 ms
RDP response median 332.4 ms
RDP response avg 350.1 ms
RDP response max 471.2 ms
```

A temporary host-specific route was added on MIPC to bypass Karing for Hermes only. Route selection moved to the physical Wi-Fi interface; real ICMP to Hermes became `85–95 ms`, avg `89 ms`, TTL 52, confirming the bypass.

The Hermes `ssh.exe` transport was deliberately killed once so the agent would reconnect over that direct route. Dashboard briefly showed MIPC offline during the intentional transport break, then recovered when the agent created a new tunnel.

Important A/B result: **after the tunnel reconnected over the direct Wi-Fi route, subjective RDP became substantially worse and the Windows RDP connection-quality indicator dropped**. Therefore the working hypothesis “Karing is the main cause of the steady-state RDP lag” is weakened; direct routing is not an improvement in this environment.

The current subjective acceptance establishes that the restored/working Hermes path is smooth enough for normal use. No further routing experiment is required before continuing current-head regression smoke.

Remaining performance-related validation is narrower:

1. explicitly exercise and verify Hermes loopback RDP classification (`Hermes=1/direct=0`) on current head;
2. verify endpoint-open/no-client classification remains `Hermes=0`;
3. test `НАБЛЮДАТЬ 60с` cadence + automatic stop.

## Stable live baseline

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- raw Win10 x64 + x86 PowerShell `Sysnative` visibility/probe;
- earlier state/endpoint/RDP classification baseline;
- current-head ordinary fast-path timing and subjective smoothness on the accepted working Hermes path.

Relevant classifier/control behavior touched by the newest fast-path refactor still needs targeted revalidation only.

## Windows Server

Confirmed old bug: installer rejected Windows Server through the client-only ProductType gate.

PR #19 allows ProductType 2/3 and has regression coverage.

Status: **IMPLEMENTED; REAL FRESH WINDOWS SERVER INSTALL PENDING**.

## Exact next engineering stage

Targeted current-head smoke, one scenario at a time. Because a Hermes RDP session is currently usable, start with:

1. **RV-002:** while connected through Hermes, dashboard must report `Hermes=1/direct=0`; this also exercises the loopback peer-correlation path;
2. **RV-003:** keep endpoint/tunnel open with no Hermes RDP client; dashboard must report `Hermes=0`;
3. **RV-001:** direct LAN/VPN RDP must report `Hermes=0/direct=1`;
4. **RV-004/RV-006:** OFF -> applied OFF + endpoint CLOSED; ON -> one tunnel + endpoint OPEN;
5. **RV-005:** exactly one Hermes `ssh.exe` in normal ON state;
6. test `НАБЛЮДАТЬ 60с` + automatic stop;
7. real fresh Windows Server install;
8. fresh patched install from Win10 x64 + PowerShell x86;
9. reconcile PR #19 with current `main`, rerun CI/recheck mergeability;
10. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not terminal transcripts. See `SESSION_PROTOCOL.md` and `CONTEXT_LIFECYCLE.md`.