# Hermes RDP — Next Work / Goal Vector

## North-star goal

Ship a stable self-hosted product where a user can:

1. install Hermes on a clean Debian/Ubuntu server;
2. add Windows PCs through Telegram;
3. paste one generated command into elevated PowerShell;
4. get a persistent endpoint per PC;
5. connect through standard Microsoft Remote Desktop from another network;
6. trust every status shown in Telegram;
7. survive reboots/network interruptions automatically;
8. update safely without losing access;
9. understand and operate the system from clear documentation.

## Already confirmed — do not redo without a regression reason

```text
Fresh OpenSSH Windows install                    PASS
External RDP over another network                PASS
Tested Windows reboot -> access recovers         PASS
Telegram OFF -> active RDP access interrupted    PASS
Telegram ON  -> RDP access restored              PASS
```

Low-level `OFF -> endpoint CLOSED` still deserves an explicit listener/port measurement, but the user-visible OFF/ON behavior is already confirmed.

## Priority 0 — do not expand scope yet

The transport works. The next risk is not “can RDP connect?” but whether the control plane tells the truth and remains deterministic under failure/recovery.

## Stage 1 — State & tunnel correctness

### Immediate objective

Make Telegram and the registry reflect reality.

### Next concrete actions

1. inspect the actual Hermes `ssh.exe` process and full command line on the tested Windows PC;
2. compare it with agent `Get-SshProcesses` matching logic;
3. fix/replace unreliable `ssh_tunnel_running` detection;
4. expose actual server endpoint/listener state;
5. separate desired access state from agent heartbeat;
6. expose command pending/result/timeout state;
7. detect/avoid duplicate or orphan Hermes SSH processes;
8. verify listener-level OFF -> CLOSED -> ON -> OPEN.

### Target state model

```text
Agent:        ONLINE | OFFLINE
Access:       ENABLED | DISABLED
Command:      IDLE | PENDING | SUCCESS | FAILED | TIMEOUT
SSH:          CONNECTED | DISCONNECTED | UNKNOWN
Endpoint:     OPEN | CLOSED | UNKNOWN
RDP sessions: N
```

Rule: `ONLINE` means agent/API heartbeat only. A device may correctly be `Agent ONLINE + Access OFF + SSH disconnected + Endpoint closed`.

## Stage 2 — Remaining reliability / recovery

Still test:

- temporary Windows network disconnect -> reconnect;
- Linux server reboot -> controller + dedicated sshd recover -> clients reconnect;
- controller restart;
- dedicated sshd restart;
- repeated reconnect without duplicate/orphan processes;
- two or more devices simultaneously;
- one device failure does not affect another.

Windows reboot recovery is already PASS.

## Stage 3 — Device/security lifecycle acceptance

Verify:

- each device has a unique Ed25519 key;
- first device key cannot bind second device endpoint;
- private key never reaches server;
- revoked key cannot authenticate;
- DELETE revokes device API token and SSH key;
- DELETE closes endpoint;
- freed port is safely reusable only after cleanup;
- administrative SSH stays independent;
- Telegram authorization remains owner-limited;
- no Defender exclusions are required.

Also verify `RESTART` means a real transport restart rather than only changing a flag.

## Stage 4 — Safe installation / migration / updates

### Legacy Windows reinstall

Replace fragile recursive old-directory backup with whole-directory archival:

```text
HermesRDP
 -> rename/move -> HermesRDP-legacy-TIMESTAMP
 -> create clean HermesRDP
```

Use scoped ACL takeover only when the move itself is denied. Pair only after local filesystem preparation succeeds.

### Pairing UX

Expired pairing codes should produce a concise, understandable retry message instead of a confusing PowerShell exception wall.

### Server update target

```text
backup
 -> stage update
 -> syntax/config checks
 -> restart
 -> health checks
 -> reconnect/endpoint smoke test
 -> COMMIT

failure
 -> rollback
 -> restart previous version
 -> verify previous health
```

### Windows client update target

```text
backup current agent
 -> install new agent
 -> parse/start checks
 -> heartbeat/tunnel health check
 -> keep update

failure
 -> restore previous agent
 -> restart task
 -> verify previous access
```

## Stage 5 — Telegram Dashboard v2

Only after state measurement is trustworthy.

Recommended device view:

```text
DEVICE NAME

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
```

Buttons:

- enabled: `DISABLE ACCESS`, `RESTART TUNNEL`;
- disabled: `ENABLE ACCESS`;
- pending: `WORKING…` and block contradictory commands;
- active session + OFF/RESTART: confirmation because the session will be disconnected.

Do not label Windows-side `127.0.0.1` as an external client.

## Stage 6 — Documentation rebuild

Use old `v1.0.7` documentation quality as the structural baseline, not its obsolete FRP implementation.

`ARCHITECTURE.md` should include:

- goals and boundaries;
- large architecture diagram;
- server/client responsibilities;
- pairing lifecycle;
- ON/OFF/RESTART lifecycle;
- state machine;
- trust chain;
- SQLite model;
- failure/recovery model;
- multi-device isolation;
- subsystem modification map.

README should restore polished badges/buttons and prominently state:

> All Windows devices are equal clients. Only the Hermes Linux server has a special infrastructure role.

Sweep all docs for stale FRP/version claims.

## Stage 7 — Website v2

Do not keep cosmetically patching the current page.

Explain product first:

```text
Windows PCs -> one Hermes server -> remote RDP clients
                    |
                    -> Telegram control
```

Then explain OpenSSH, per-device Ed25519 isolation, pinning, persistent endpoints, telemetry and self-hosted security.

## Stage 8 — Final acceptance matrix

```text
Clean server install                  PASS
Windows fresh install                 PASS
Legacy Windows reinstall              TODO
External RDP over another network     PASS
Device #1                             PASS
Device #2                             PARTIAL / formal acceptance TODO
Unique ports                          OBSERVED / formal isolation TODO
Unique SSH keys                       TODO formal proof
Cross-port key isolation              TODO

OFF -> RDP access interrupted         PASS
ON -> RDP access restored             PASS
OFF -> endpoint measured closed       TODO
ON -> endpoint measured open          TODO
RESTART -> transport recreated        TODO
DELETE -> token/key revoked           TODO
DELETE -> endpoint closed             TODO
Freed port reuse                      TODO

Windows reboot                        PASS
Server reboot                         TODO
Network loss/reconnect                TODO
Controller restart                    TODO
SSHD restart                          TODO

Server update                         TODO
Server automatic rollback             TODO
Client update                         TODO
Client automatic rollback             TODO

Docs consistency                      TODO
README                                TODO
Website                               TODO
Linux CI                              verify current
Windows PowerShell CI                 verify current
Release automation                    verify current
```

## Release target

**Hermes RDP v1.2.0 — Stabilization**

Implementation order:

1. truthful state + command lifecycle;
2. remaining recovery/security/delete/update acceptance;
3. Dashboard v2;
4. docs/README rebuild;
5. Website v2;
6. full acceptance + release.

Critical correctness fixes may ship as `v1.1.x` patches first.
