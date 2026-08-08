# Hermes RDP — Current State Snapshot

Snapshot date: 2026-08-08

For the hottest operational state read `ACTIVE_WORK.md` first. For individual acceptance facts read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Active stabilization PR: **#19**, branch `fix/control-state-dashboard`.
- Current PR head at this snapshot: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Target release: **v1.2.0 — Stabilization**.
- Draft release notes are maintained on the active branch in `docs/releases/v1.2.0-draft.md`.
- Product changes from PR #19 are not merged to `main` yet.

## Architecture — confirmed

Hermes RDP uses:

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd
      |
reverse Microsoft OpenSSH tunnels
      |
Windows RDP :3389
      |
persistent public endpoint per device
```

Durable boundaries:

- all Windows PCs are equal clients;
- only the Linux Hermes server has the special infrastructure role;
- administrative SSH remains separate;
- FRP is not part of the active runtime;
- private per-device SSH key stays on Windows;
- server stores/restricts the public key to its assigned endpoint;
- Telegram is control plane, not RDP transport;
- agent heartbeat must remain available while RDP access is OFF.

## Live-confirmed product behavior

### Core transport

- fresh OpenSSH Windows installation on the normal tested path — PASS;
- external RDP over another network — PASS;
- Windows reboot -> Hermes agent/tunnel recovers -> RDP usable — PASS.

### Telegram OFF / ON

- OFF interrupts active RDP access — PASS;
- ON restores access — PASS;
- tested OFF state can remain `Agent online + access off + SSH disconnected + endpoint closed` — PASS.

### Server endpoint truth

The old Windows-side public-port self-probe could false-positive when the Windows route used a VPN/TUN/proxy path.

Current branch moved public endpoint truth to the Linux server listener (`/proc/net/tcp*`). Live acceptance showed:

```text
OFF -> assigned listener CLOSED
ON  -> assigned listener OPEN
```

PASS on the tested branch build.

### RDP channel truth

The Windows agent and Telegram now distinguish actual RDP transport:

```text
direct LAN/VPN remote address -> direct RDP
loopback RDP whose peer is the Hermes ssh.exe -> Hermes RDP
```

Live acceptance:

```text
direct RDP  -> Hermes=0, LAN/VPN=1  PASS
Hermes RDP  -> Hermes=1, LAN/VPN=0  PASS
```

An open SSH tunnel/endpoint alone does not count as an active Hermes RDP session.

### Control-state model

Current branch separates:

- agent heartbeat;
- desired RDP access;
- agent-applied access state;
- SSH process/transport state;
- server endpoint state;
- RDP channel activity;
- pending/last command state.

The earlier contradiction `ONLINE + tunnel stopped while RDP works` has been addressed on the tested branch rather than treated as a transport failure.

## Windows compatibility

### Win10 x64 + x86 PowerShell

Confirmed real environment:

```text
64-bit Windows
32-bit PowerShell process under SysWOW64
Microsoft OpenSSH capability installed
System32 lookup redirected
Sysnative reaches native OpenSSH binaries
```

PR #19 implements the native resolver:

- x64 process -> `System32`;
- x86 process on x64 OS -> `Sysnative` for native probing/keygen;
- config stores canonical `System32` SSH path;
- no PATH/Git-SSH fallback.

Runtime `Sysnative` behavior is PASS. Full patched **fresh install from x86 PowerShell** is still a final acceptance item.

### Existing-install safety

A previous duplicate `Добавить ПК` attempt could stop the working task/SSH before pairing failed on reused identity/port.

PR #19 adds an existing-valid-install guard before destructive actions. Live tested on Win10:

- Task remains Running;
- exactly one Hermes SSH process remains;
- device identity and RDP port remain unchanged.

PASS.

### Windows Server

Confirmed bug: installer rejected Windows Server with `ProductType != 1` even though the following edition check included Server.

PR #19 now allows supported Windows Server `ProductType` 2/3 and has regression coverage.

Status: **IMPLEMENTED, NOT LIVE VALIDATED**. Real fresh Windows Server installation remains required.

## Performance stabilization

A performance regression was found after adding richer RDP/SSH telemetry.

Real MIPC timings before optimization:

```text
all Established TCP connections   ~1059 ms
RDP-only TCP query                ~516 ms
full Win32_Process query          ~357 ms
TOP-process sampling window       800 ms minimum
```

The old 3-second telemetry loop could spend most of the interval collecting diagnostics, matching observed RDP micro-freezes.

PR #19 now implements a cost-tiered telemetry model:

```text
FAST / ~3s
heartbeat + command polling + access + SSH + RDP channel

BACKGROUND / ~15s
CPU + RAM + disk + network + sessions + route + uptime

OBSERVE 60s
resources ~3s
TOP processes ~6s
Telegram live refresh ~3s
then automatic stop
```

Also implemented:

- no full Established TCP-table scan in normal RDP classification;
- exact/limited socket queries where possible;
- SSH process lookup narrowed and reused inside the cycle;
- TOP processes disabled in normal background operation;
- Telegram no longer performs endless 3-second live redraw by default.

Status: **IMPLEMENTED, CI PASS, NOT YET LIVE PERFORMANCE ACCEPTED**.

## Telegram UX on active branch

Implemented:

- Russian user-facing state vocabulary (`В СЕТИ`, `ПОДКЛЮЧЕН`, `ОТКРЫТ`, etc.);
- separate `RDP через Hermes` and `RDP напрямую (LAN/VPN)` counters;
- contextual ON/OFF/RESTART controls;
- pending command state;
- explicit `НАБЛЮДАТЬ 60с` instead of permanent LIVE polling.

The RDP channel counters are live-accepted. The latest observation/performance/localization server-side build still needs deployment/live acceptance.

## CI

Current PR branch has passing Linux and Windows CI for the latest stabilization work.

Important evidence boundary:

- CI PASS = source/static/regression checks pass;
- Windows Server install, telemetry performance and observation auto-off still require real runtime acceptance.

## What is deployed

A pre-latest PR build is deployed and has passed live:

- OFF/ON state correctness;
- endpoint CLOSED/OPEN truth;
- RDP Hermes/direct classification.

The newest performance scheduling, `НАБЛЮДАТЬ 60с`, latest localization and Windows Server installer changes are **not yet considered live-deployed/accepted** in this snapshot.

## Open acceptance / blockers

Immediate PR #19 gate:

1. deploy latest server-side branch code with backup;
2. update MIPC agent without changing identity/key/port;
3. benchmark new loop and verify RDP micro-freezes disappear/materially reduce;
4. test `НАБЛЮДАТЬ 60с` including automatic stop;
5. real fresh install on Windows Server;
6. real fresh install Win10 x64 from x86 PowerShell.

After PR #19 stabilization:

- RESTART transport recreation acceptance;
- network-loss reconnect;
- Linux server reboot recovery;
- controller / dedicated sshd restart recovery;
- repeated reconnect without duplicates/orphans;
- multi-device key/endpoint isolation;
- DELETE/revoke/endpoint cleanup/port reuse;
- legacy protected-ACL migration;
- robust server/client update health checks + automatic rollback;
- documentation/README rebuild;
- Website v2;
- final release acceptance.

## Context reliability

As of 2026-08-08 the context model is continuous rather than end-of-chat only.

Use:

- `ACTIVE_WORK.md` for hot operational truth;
- `EVIDENCE_LEDGER.md` for durable acceptance evidence;
- this file for consolidated product state;
- `SESSION_PROTOCOL.md` for checkpoint triggers.

Do not rely on `LAST_SESSION.md` alone.