# Hermes RDP — Latest Product Audit

Audit date: 2026-08-07
Updated after real reboot + ON/OFF validation: 2026-08-07

This file preserves the main conclusions from the last long-chat analysis and records which earlier uncertainties were later resolved by testing.

## Executive summary

The core product works:

- Windows devices register;
- persistent endpoints are allocated;
- OpenSSH reverse transport works;
- Telegram receives telemetry;
- real RDP access from an external mobile network works;
- tested Windows reboot recovery works;
- Telegram OFF/ON works at the user-visible RDP level.

Therefore the project should not search for a new transport. The next phase is **stabilizing the control plane, observability and recovery guarantees**.

The most important remaining product bug is that Telegram can show transport state that contradicts reality.

## Post-audit validation results

After the initial audit, the user performed additional live tests.

### Windows reboot

The Windows PC was rebooted. After startup/reconnect, RDP access worked again.

Result:

```text
Windows reboot -> automatic Hermes recovery -> RDP usable
PASS
```

This closes the tested Windows-reboot scenario unless future changes regress it.

### Telegram OFF / ON

With RDP working:

```text
OFF -> active RDP session disconnected / access became unusable
ON  -> RDP access became usable again
```

The user explicitly confirmed the functionality works.

Result:

```text
OFF -> user-visible RDP access interrupted    PASS
ON  -> user-visible RDP access restored       PASS
```

Evidence boundary: the final test did not independently probe the public port/listener during OFF, so keep `OFF -> endpoint measured CLOSED` as a separate low-level acceptance item.

## Dashboard problem still open

Earlier device views showed contradictory combinations such as:

```text
Agent/device: ONLINE
SSH tunnel: stopped
Endpoint/RDP: actually usable
```

The later successful ON/OFF tests do not invalidate this bug. They clarify it:

> control behavior works, but telemetry/representation can be wrong.

This distinction is critical. Do not debug a working transport merely because an unreliable status field says `stopped`.

## Correct conceptual state model

Hermes needs separate state dimensions:

```text
1. Agent heartbeat
   ONLINE / OFFLINE

2. Desired RDP access
   ENABLED / DISABLED

3. Command lifecycle
   IDLE / PENDING / SUCCESS / FAILED / TIMEOUT

4. Actual SSH transport
   CONNECTED / DISCONNECTED / UNKNOWN

5. Public endpoint
   OPEN / CLOSED / UNKNOWN

6. RDP activity
   N sessions
```

A normal disabled device should still be:

```text
Agent            ONLINE
RDP access       DISABLED
SSH tunnel       DISCONNECTED
Endpoint         CLOSED
```

The agent must stay ONLINE so it can poll the API and receive the next ON command.

## Why `SSH tunnel: stopped` remains suspicious

Current Windows agent `Get-SshProcesses` uses a strict `Win32_Process.CommandLine` match. The installer historically used a looser process check.

Likely failure mode:

```text
real ssh.exe is healthy
 -> installer check finds it
 -> agent telemetry matcher misses it
 -> Telegram says tunnel stopped
 -> RDP still works
```

This is still **LIKELY**, not confirmed. Inspect the actual Hermes `ssh.exe` process command line on the tested Windows machine before patching.

Also rule out duplicate/orphan/legacy SSH processes.

## Command lifecycle issue

Telegram currently communicates that a command was sent more clearly than whether it completed.

Target lifecycle:

```text
queued -> delivered -> executing -> success / failed / timeout
```

The registry already contains command-related state that can support a better UI. Dashboard v2 should show the final result and measured state instead of treating callback acknowledgement as completion.

## Listener-level OFF/ON test still useful

User-visible OFF/ON is now PASS, but the engineering acceptance matrix should still explicitly measure:

```text
access ON
 -> endpoint measured OPEN
 -> OFF
 -> endpoint measured CLOSED
 -> ON
 -> endpoint measured OPEN
```

This verifies exact server listener cleanup and supports later DELETE/revoke testing.

## Pairing-code UX observation

One install attempt failed because the pairing code had expired. A fresh valid pairing flow subsequently succeeded.

The architecture is fine; the UX should improve. An expired code should lead to a short actionable retry message rather than a large PowerShell exception.

## Legacy Windows installer bug

A real reinstall over an old protected Hermes/WinMon/FRP directory previously failed while recursively copying a protected key.

Desired migration:

```text
stop old tasks/processes
 -> move/rename whole HermesRDP directory to sibling archive
 -> scoped takeown/icacls only if move is denied
 -> create clean HermesRDP
 -> generate fresh key
 -> pair/install
```

Re-check current source/branch status before implementing because documentation can be ahead of merged code.

## Remaining reliability gaps

Already resolved in real testing:

- Windows reboot recovery: PASS;
- external RDP: PASS;
- OFF/ON user-visible behavior: PASS.

Still required:

- Windows network-loss reconnect;
- Linux server reboot recovery;
- controller restart behavior;
- dedicated sshd restart behavior;
- duplicate/orphan SSH prevention;
- two-device isolation proof;
- RESTART semantics;
- DELETE + key/token revoke;
- DELETE endpoint cleanup;
- safe port reuse;
- update runtime validation;
- automatic rollback.

## Dashboard v2 proposal

Top of device screen:

```text
DEVICE NAME
Windows machine / OS

STATUS
Agent            ONLINE
RDP access       ENABLED
SSH tunnel       CONNECTED
Endpoint         OPEN :PORT
RDP sessions     1

Last command
ON · SUCCESS · 2 sec ago
```

Then resources and sessions.

Buttons should be state-driven:

- enabled -> `DISABLE ACCESS`, `RESTART TUNNEL`;
- disabled -> `ENABLE ACCESS`;
- pending -> `WORKING…` and block contradictory actions;
- active RDP + OFF/RESTART -> confirmation because the operation disconnects the session.

Do not call Windows-side `127.0.0.1` an external client. If true source IP visibility is required, observe it server-side before forwarding.

## Documentation / README conclusion

The user's criticism remains valid.

Older `v1.0.7` docs had stronger:

- system-boundary explanations;
- Mermaid diagrams;
- pairing/command sequences;
- trust flow;
- data model;
- failure/recovery discussion.

The OpenSSH documentation should regain that depth without restoring obsolete FRP concepts.

README should regain polished badges/links and prominently state:

> all Windows clients are equal; only the Linux Hermes server is special.

## Website conclusion

Current site is functional but interim.

Do not spend the stabilization cycle on cosmetic patches. Website v2 should come after truthful state and reliability.

First-screen product explanation:

```text
Home PC ----\
Office PC ----> Hermes Server ----> Remote Desktop
Laptop ------/       |
                     +---- Telegram control
```

Implementation/security details such as OpenSSH, Ed25519 and pinning come after the user understands the product.

## Project vector after audit

Hermes RDP is:

> A self-hosted multi-PC remote-access system with one Linux gateway, persistent per-device endpoints, secure automatic pairing, monitoring and Telegram control.

Not merely a tunnel script.

## Recommended next milestone

**Hermes RDP v1.2.0 — Stabilization**

Order:

1. truthful SSH/endpoint/command state;
2. remaining recovery + lifecycle + update/rollback acceptance;
3. Telegram Dashboard v2;
4. docs + README rebuild;
5. Website v2;
6. full acceptance + release.

## Immediate next action from this audit

Inspect the actual Hermes `ssh.exe` command line on the tested Windows PC and compare it with `Get-SshProcesses`. Fix measured state before redesigning the dashboard around unreliable telemetry.
