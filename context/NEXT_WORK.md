# Hermes RDP — Next Work / Goal Vector

## North-star goal

Ship a stable self-hosted product where a user can:

1. install Hermes on a clean Debian/Ubuntu server;
2. open Telegram;
3. press “Add PC”;
4. paste one generated command into elevated Windows PowerShell;
5. see the device appear with a persistent endpoint;
6. connect via standard Microsoft Remote Desktop from another network;
7. trust every status shown in Telegram;
8. survive reboots/network interruptions automatically;
9. update safely without losing working access;
10. understand and operate the system from clear documentation.

## Priority 0 — do not expand scope yet

Until the stabilization acceptance passes, avoid unrelated new features. The transport already works; the main risk is making the control plane look finished while its state semantics are still ambiguous.

## Stage 1 — State & tunnel correctness

### Objective

Make Telegram and the registry reflect reality.

### Required work

- separate `agent_online` from `access_enabled`;
- expose desired access state from registry;
- expose command pending/result state;
- fix or replace unreliable `ssh_tunnel_running` detection;
- obtain actual server endpoint/listener state;
- define command timeout behavior;
- detect/avoid orphan Hermes `ssh.exe` processes;
- validate server-side `close_tunnel` behavior against real sshd children;
- ensure OFF cannot leave a reachable endpoint while UI says disabled;
- ensure ON does not report success before endpoint is actually reachable;
- ensure RESTART means a real transport restart, not only re-queueing a flag.

### Target state model

```text
Agent:        ONLINE | OFFLINE
Access:       ENABLED | DISABLED
Command:      IDLE | PENDING | SUCCESS | FAILED | TIMEOUT
SSH:          CONNECTED | DISCONNECTED | UNKNOWN
Endpoint:     OPEN | CLOSED | UNKNOWN
RDP sessions: N
```

### UI rule

`ONLINE` describes the agent/API heartbeat only. A device may correctly be:

```text
Agent ONLINE + Access OFF + SSH disconnected + Endpoint closed
```

## Stage 2 — Telegram Dashboard v2

Only after state is trustworthy.

### Device view

Recommended structure:

```text
Device name / Windows machine

STATUS
Agent            ONLINE
RDP access       ENABLED
SSH tunnel       CONNECTED
Endpoint         OPEN :PORT
RDP sessions     1

Last command
ON · SUCCESS · 2 sec ago

RESOURCES
CPU / RAM / Disk / Network / Uptime

SESSIONS
Windows sessions / RDP session count
```

### Buttons

When access is enabled:

```text
DISABLE ACCESS
RESTART TUNNEL
```

When disabled:

```text
ENABLE ACCESS
```

When command is pending:

```text
WORKING…
```

Avoid contradictory button presses while one command is pending.

If an active RDP session exists, OFF/RESTART should request confirmation because the operation will disconnect it.

### Remove misleading field

Do not call Windows-side `127.0.0.1` an “external client”. If external source IP visibility is desired, implement it server-side.

## Stage 3 — Reliability / recovery

Acceptance tests:

- Windows reboot -> agent starts -> SSH returns -> endpoint returns;
- Windows network disconnect -> reconnect;
- server reboot -> both Hermes services start -> clients reconnect;
- controller restart -> existing SSH transport behavior remains sane;
- dedicated sshd restart -> clients reconnect;
- repeated reconnect does not spawn duplicate/orphan processes;
- two or more devices operate simultaneously;
- one device failure does not affect others.

## Stage 4 — Safe installation / migration / updates

### Windows reinstall

Replace fragile recursive legacy backup with whole-directory archival:

```text
HermesRDP
   -> rename/move -> HermesRDP-legacy-TIMESTAMP
   -> create clean HermesRDP
```

Scoped ACL fallback only if required.

Pairing starts only after the local filesystem is ready.

### Server update

Desired flow:

```text
backup
 -> stage update
 -> syntax/config checks
 -> restart
 -> health checks
 -> endpoint/reconnect smoke check
 -> COMMIT

failure at any step
 -> rollback backup
 -> restart previous version
 -> verify previous health
```

### Windows client update

Desired flow:

```text
backup current agent
 -> install new agent
 -> parse check
 -> start
 -> heartbeat/tunnel health check
 -> keep update

failure
 -> restore old agent
 -> restart old task
 -> verify old tunnel
```

## Stage 5 — Security/operational acceptance

Verify:

- each device has unique Ed25519 key;
- first device key cannot bind second device endpoint;
- private keys never reach server;
- revoked key cannot authenticate;
- device API token is revoked on DELETE;
- freed port is reusable only after revoke/cleanup;
- administrative server SSH remains independent;
- Telegram authorization is limited to configured owner;
- secrets are absent from logs/docs/examples;
- no Microsoft Defender exclusions are required.

## Stage 6 — Documentation rebuild

Use old `v1.0.7` documentation quality as the structural baseline, not its obsolete FRP implementation.

### ARCHITECTURE.md should contain

- product goals;
- system boundaries;
- large overview diagram;
- component diagram;
- server responsibility;
- Windows responsibility;
- lifecycle of pairing;
- lifecycle of ON/OFF/RESTART;
- state machine;
- trust chain;
- SQLite model;
- failure/recovery model;
- multi-device isolation;
- where to modify each subsystem.

Prefer Mermaid plus readable text/ASCII diagrams.

### README

Restore polished badges/buttons:

- Latest Release;
- CI;
- MIT;
- Windows;
- Debian/Ubuntu;
- Website;
- Documentation.

Restore the key rule prominently:

> All Windows devices are equal clients. Only the Hermes Linux server has a special infrastructure role.

### Documentation consistency

Sweep every file for stale FRP concepts and version state.

## Stage 7 — Website v2

Do not simply patch the current page.

The website should explain the problem/solution first:

```text
Windows PCs -> one Hermes server -> remote RDP clients
                    |
                    -> Telegram control
```

Then explain:

- persistent endpoints;
- multi-device management;
- no inbound port forwarding on remote Windows routers;
- OpenSSH transport;
- per-device Ed25519 isolation;
- Telegram control and telemetry;
- self-hosted security boundaries;
- quick deployment.

Design goals:

- visual architecture as a central element;
- less generic landing-page copy;
- more credible engineering/product identity;
- clear documentation/release links;
- strong desktop and mobile layout;
- no fake UI claims that do not match the real bot.

## Stage 8 — Final acceptance

The release is stable only after this matrix passes:

```text
Clean server install                  PASS
Windows fresh install                 PASS
Legacy Windows reinstall              PASS
External RDP over another network     PASS
Device #1                             PASS
Device #2                             PASS
Unique ports                          PASS
Unique SSH keys                       PASS
Cross-port key isolation              PASS

OFF -> endpoint closed                PASS
ON -> endpoint restored               PASS
RESTART -> transport recreated        PASS
DELETE -> token/key revoked           PASS
DELETE -> endpoint closed             PASS
Freed port reuse                      PASS

Windows reboot                        PASS
Server reboot                         PASS
Network loss/reconnect                PASS
Controller restart                    PASS
SSHD restart                          PASS

Server update                         PASS
Server automatic rollback             PASS
Client update                         PASS
Client automatic rollback             PASS

Docs consistency                      PASS
README                                PASS
Website                               PASS
Linux CI                              PASS
Windows PowerShell CI                 PASS
Release automation                    PASS
```

## Release target

Recommended coherent milestone:

**Hermes RDP v1.2.0 — Stabilization**

Suggested implementation order:

1. state/tunnel correctness;
2. reliability and rollback;
3. Dashboard v2;
4. docs/README rebuild;
5. Website v2;
6. full acceptance and release.

Critical correctness bugs may be shipped as `v1.1.x` patches before the full `v1.2.0` milestone.