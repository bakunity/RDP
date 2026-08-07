# Hermes RDP — Project Handoff

Last updated: 2026-08-07

## 1. Product vector

Hermes RDP is a self-hosted **multi-PC remote-access control plane**:

> One public Linux server provides controlled remote RDP access to multiple Windows PCs. Every PC gets its own persistent endpoint, credentials and state; pairing, monitoring and control are available through Telegram.

OpenSSH is the current transport implementation. The product is not an SSH wrapper and should not be treated as an FRP project.

## 2. Current architecture

```text
Telegram user
     |
     v
Hermes Controller/API + SQLite + command queue
     |
     +---- dedicated Hermes sshd
                 |
        reverse OpenSSH tunnels
          /              \
   Windows PC #1      Windows PC #2 ...
   RDP 3389           RDP 3389
          \              /
        persistent public endpoints
                 |
          standard RDP client
```

Server side:

- `hermes-rdp.service`: HTTPS API + Telegram bot + SQLite registry;
- `hermes-rdp-sshd.service`: isolated OpenSSH daemon for reverse forwarding;
- administrative SSH on port 22 remains separate;
- RDP endpoint pool defaults to `53389–53420`.

Windows side:

- built-in `ssh.exe` and `ssh-keygen.exe`;
- `HermesRdpAgent.ps1` runs from Scheduled Task as `SYSTEM`;
- each PC gets its own Ed25519 keypair, API token, device ID and persistent RDP endpoint;
- private SSH key stays on Windows;
- server stores only the public key and authorizes only the assigned endpoint via `permitlisten`;
- API certificate is pinned;
- SSH host key is delivered through the pinned API and stored in dedicated `known_hosts`.

## 3. Architecture history

```text
reverse RDP idea
 -> FRP prototype
 -> multi-PC registry + Telegram + pairing
 -> Defender operational problem with FRP Windows binary
 -> FRP removed
 -> Windows system OpenSSH
 -> isolated server sshd
 -> per-device Ed25519 keys + permitlisten
 -> SSH host-key pinning
 -> real external RDP PASS
 -> reboot recovery PASS
 -> Telegram OFF/ON behavioral PASS
 -> stabilization phase
```

`v1.1.0` is the published OpenSSH transition release.

## 4. Confirmed real-world results

The following are no longer theoretical:

- clean OpenSSH-based Windows install completed;
- real RDP connection worked from a phone over mobile data;
- devices can be added and assigned persistent ports;
- tested Windows reboot recovered automatically and RDP became usable again;
- Telegram **OFF** disconnected an active RDP session;
- Telegram **ON** restored RDP access;
- the user explicitly confirmed ON/OFF functionality works.

Important evidence nuance:

```text
OFF -> user-visible RDP access interrupted     PASS
ON  -> user-visible RDP access restored        PASS
Windows reboot -> access recovers              PASS
OFF -> endpoint independently port-probed CLOSED   not separately proven in final test
```

Do not repeat basic “does reverse OpenSSH RDP work?” testing unless a relevant change could have regressed it.

## 5. Main open product bug: truthful state

Telegram can still show contradictory telemetry such as:

```text
Agent ONLINE
SSH tunnel: stopped
RDP/endpoint actually usable
```

This is now clearly an **observability/state-model bug**, not evidence that the transport itself is broken.

Hermes must represent these states independently:

```text
Agent heartbeat     ONLINE / OFFLINE
Desired access      ENABLED / DISABLED
Command lifecycle   IDLE / PENDING / SUCCESS / FAILED / TIMEOUT
SSH transport       CONNECTED / DISCONNECTED / UNKNOWN
Public endpoint     OPEN / CLOSED / UNKNOWN
RDP sessions        N
```

A valid disabled device should remain:

```text
Agent ONLINE
Access DISABLED
SSH DISCONNECTED
Endpoint CLOSED
```

The agent stays ONLINE so it can receive the next ON command.

## 6. Likely telemetry root cause to verify

`HermesRdpAgent.ps1` identifies Hermes SSH processes with a stricter `Win32_Process.CommandLine` match than the installer uses for its post-install check.

Likely scenario:

- real `ssh.exe` is running correctly;
- installer recognizes it;
- agent telemetry matcher does not;
- dashboard reports `SSH tunnel: stopped` even while RDP works.

This is a **LIKELY** cause, not confirmed. Inspect the actual tested Windows `ssh.exe` command line before patching. Also rule out orphan/legacy SSH processes.

## 7. Command semantics / Dashboard v2

Current command flow stores enough data for a better UX (`enabled`, pending command, sequence/result data), but Telegram mostly communicates “command sent” rather than the lifecycle of the command.

Target progression:

```text
queued -> delivered -> executing -> success / failed / timeout
```

Recommended device block:

```text
AGENT            ONLINE
RDP ACCESS       ENABLED / DISABLED
SSH TUNNEL       CONNECTED / DISCONNECTED / UNKNOWN
ENDPOINT         OPEN / CLOSED / UNKNOWN
RDP SESSIONS     N active
LAST COMMAND     success / failed / pending + timestamp
```

Buttons should be contextual and contradictory commands should be prevented while one is pending.

The old `External clients = 127.0.0.1` concept is misleading because Windows sees SSH-forwarded RDP locally. Real source IP, if needed, must be observed server-side before forwarding.

## 8. Pairing UX observation

One installation attempt failed with `pair code expired`. A fresh valid pairing flow later completed successfully.

This is not a transport failure. The installer/UI should eventually explain expired pairing codes cleanly and provide a straightforward retry path instead of surfacing a confusing PowerShell exception wall.

## 9. Legacy Windows ACL installer defect

A real upgrade from an old Hermes/WinMon/FRP directory previously failed because recursive backup attempted to read a protected legacy key.

Desired fix:

```text
stop old tasks/processes
 -> rename/move whole old Hermes directory to sibling legacy archive
 -> scoped takeown/icacls only if move is denied
 -> create clean HermesRDP directory
 -> only then pair/install
```

A branch named `fix/windows-legacy-acl-backup` existed earlier, but merge status must be rechecked before relying on it.

## 10. Remaining reliability / security acceptance

Already PASS:

- clean server/OpenSSH architecture;
- fresh Windows install;
- external-network RDP;
- tested Windows reboot recovery;
- user-visible OFF/ON access behavior.

Still required:

- temporary Windows network loss -> reconnect;
- Linux server reboot -> services + endpoints recover;
- controller restart behavior;
- dedicated sshd restart behavior;
- repeated reconnect without duplicate/orphan SSH processes;
- two+ devices simultaneously with isolation;
- first device key cannot claim second device endpoint;
- RESTART actually recreates transport;
- DELETE revokes API token + SSH key;
- DELETE closes endpoint;
- safe freed-port reuse;
- low-level endpoint CLOSED/OPEN measurement around OFF/ON;
- safe server update + automatic rollback;
- safe Windows client update + automatic rollback;
- legacy reinstall path.

## 11. Documentation / README / website audit

The user does not consider the current public documentation/site final.

Documentation issues found:

- older `v1.0.7` architecture docs were much richer in diagrams, sequences, trust flow and failure behavior;
- current OpenSSH docs became shorter and lost explanatory structure;
- some development/roadmap/website docs still contained stale FRP/version wording during the audit;
- README lost useful badges/buttons and the strong architecture presentation.

Required direction: restore the **clarity and structure** of the old docs while keeping all technical content OpenSSH-correct.

Key product principle to state prominently:

> All Windows PCs are equal clients. Only the Linux Hermes server has the special infrastructure role.

Website v2 should explain the product before implementation details:

```text
Home PC ----\
Office PC ----> Hermes Server ----> Remote Desktop from anywhere
Laptop ------/       |
                     +---- Telegram control
```

Do not prioritize a cosmetic website rebuild before state correctness and remaining reliability work.

## 12. Release direction

Project phase: **stabilization**, not feature discovery.

Recommended coherent target:

**Hermes RDP v1.2.0 — Stabilization**

Order:

1. fix truthful state / SSH telemetry / command lifecycle;
2. finish recovery + delete/isolation + update/rollback acceptance;
3. build Telegram Dashboard v2 on measured state;
4. rebuild docs + README;
5. Website v2;
6. full acceptance + release.

Critical correctness fixes can ship as `v1.1.x` patches.

## 13. Immediate next engineering target

Do this before unrelated work:

1. inspect actual Hermes `ssh.exe` process command line on the tested Windows PC;
2. compare it with `Get-SshProcesses` matching logic;
3. fix measured SSH state;
4. obtain/represent measured endpoint state;
5. expose command result lifecycle in Telegram;
6. then implement Dashboard v2.

## 14. Working style for future chats

- Russian;
- direct technical discussion;
- one live infrastructure stage at a time;
- copy-paste commands instead of manual `nano`/`vim` editing;
- explicit verification after each stage;
- do not claim PASS without output/user evidence;
- separate rollback command/plan where practical;
- do not weaken Microsoft Defender;
- do not reintroduce FRP;
- do not expose secrets in diagnostics/context;
- keep documentation visual, explanatory and coherent.
