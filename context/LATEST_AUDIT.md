# Hermes RDP — Latest Product Audit

Audit date: 2026-08-07

This file preserves the main conclusions from the last long-chat analysis before migrating to a new conversation.

## Executive summary

The core product already works:

- Windows devices can be registered;
- persistent ports are allocated;
- OpenSSH reverse transport works;
- Telegram receives telemetry;
- real RDP access from an external mobile network has been confirmed;
- multiple devices/ports are now being used.

The project should therefore stop behaving like a prototype that is still searching for a transport. The next phase is **stabilizing the control plane**.

The most important issue is that the Telegram dashboard currently cannot be trusted as a precise representation of tunnel/access state.

## Dashboard problem observed

The device page has shown states like:

```text
Agent/device: ONLINE
SSH tunnel: stopped
Endpoint: available
RDP connections: 1
```

The same kind of display was seen around ON and OFF operations while actual ports/RDP remained operational.

The dashboard currently makes it hard to understand what changed after pressing ON/OFF.

## Correct conceptual state model

Do not use one green/red status for everything.

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

A normal disabled device should still look like:

```text
Agent            ONLINE
RDP access       DISABLED
SSH tunnel       DISCONNECTED
Endpoint         CLOSED
```

Keeping the agent ONLINE is necessary because the agent needs to poll the API and receive a future ON command.

## Why `SSH tunnel: stopped` is suspicious

Current Windows agent function `Get-SshProcesses` identifies Hermes SSH only if `Win32_Process.CommandLine` contains both the configured key path and the exact reverse-forward text.

The Windows installer uses a looser check after installation and accepts an `ssh.exe` process containing only the expected key path.

Therefore the same real process can plausibly pass installer verification and fail telemetry detection.

This is currently a **likely cause**, not yet a proven final root cause. Verify the real command line/process behavior on the test Windows machine.

Also check for orphan/legacy SSH processes.

## OFF is not accepted until endpoint is actually closed

Current Telegram behavior queues the command and shows a callback that the command was sent. That is not sufficient.

The expected OFF result is:

```text
Agent ONLINE
Access DISABLED
SSH disconnected
Endpoint CLOSED
```

If endpoint remains open, trace the full chain:

```text
Telegram
 -> Registry command
 -> Windows telemetry poll
 -> Windows command execution
 -> Stop-SshTunnel
 -> command-result
 -> server listener close
 -> refreshed measured state
```

The registry already stores command sequence, pending command and last result; Dashboard v2 should use this data.

## Server-side tunnel close needs a real integration test

The server helper attempts to find the listener PID and terminate it when it belongs to `/usr/sbin/sshd`.

Static tests exist for this logic, but a real acceptance test is needed:

```text
start reverse SSH
 -> endpoint OPEN
 -> OFF
 -> sshd child/listener disappears
 -> endpoint CLOSED
 -> ON
 -> new reverse SSH
 -> endpoint OPEN
```

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

Then CPU/RAM/disk/network/uptime/processes.

Buttons should depend on current state:

Enabled:

```text
DISABLE ACCESS
RESTART TUNNEL
```

Disabled:

```text
ENABLE ACCESS
```

Pending:

```text
WORKING…
```

OFF/RESTART should request confirmation when an RDP session is active.

## Misleading `External clients` field

Windows sees the forwarded RDP connection locally through SSH and may report `127.0.0.1`. This is not the real external client address.

Either rename/remove the field or implement source-address observation on the Linux server before forwarding.

## Legacy Windows installer bug

A real reinstall over an old protected Hermes/WinMon/FRP directory failed while recursively copying a protected private-key file.

Current desired migration design:

```text
stop old tasks/processes
 -> move entire HermesRDP directory to sibling legacy archive
 -> scoped takeown/icacls only if move is denied
 -> create clean HermesRDP
 -> generate new key
 -> only then pair
```

The current main installer must be rechecked because documentation already describes this intended behavior even though the source was still seen using recursive `Copy-Item` during the audit.

## Reliability gaps

Still required before “stable”:

- Windows reboot recovery;
- Windows network reconnect;
- Linux server reboot recovery;
- controller/sshd restart behavior;
- two-device isolation tests;
- OFF/ON/RESTART;
- DELETE;
- key/token revoke;
- endpoint close;
- safe port reuse;
- update runtime validation;
- automatic rollback.

## Documentation audit conclusion

The user's criticism is supported by the repository.

The old `v1.0.7` documentation had stronger architecture explanations:

- clear product goals;
- system boundaries;
- Mermaid diagrams;
- pairing sequence;
- command sequence;
- trust flow;
- data model;
- failure/recovery explanation.

The newer OpenSSH docs became shorter and lost much of this structure.

Additionally, several current docs were found stale/inconsistent during the audit:

- `DEVELOPMENT.md` still referred to FRPS/FRPC rules;
- `ROADMAP.md` still contained FRP-specific future work;
- `WEBSITE.md` still contained old version/FRP maintenance wording;
- README release wording was stale because `v1.1.0` had already been published.

The fix is not to restore FRP text. Restore the **clarity/structure** of the old documentation while describing the OpenSSH system accurately.

## README conclusion

Restore the polished top-level project presentation from the older README:

- Latest Release badge;
- CI badge;
- MIT badge;
- Windows badge;
- Debian/Ubuntu badge;
- prominent Website / Docs / Release links;
- strong architecture diagram.

Also restore the key product principle:

> all Windows clients are equal; only the Linux Hermes server is special.

## Website conclusion

The current site is technically functional but is not accepted as the final product presentation.

Do not continue endless cosmetic patches. Build Website v2 after product behavior is stabilized.

The site should explain the product first, implementation second:

```text
Home PC ----\
Office PC ----> Hermes Server ----> Remote Desktop
Laptop ------/       |
                     +---- Telegram control
```

OpenSSH/Ed25519/pinning belong in later architecture/security sections.

## Project vector after audit

Hermes RDP should be treated as:

> A self-hosted multi-PC remote-access system with one Linux gateway, persistent per-device endpoints, secure automatic pairing, monitoring and Telegram control.

Not merely a tunnel script.

## Recommended next milestone

**Hermes RDP v1.2.0 — Stabilization**

Suggested order:

1. State & tunnel correctness.
2. Recovery/update/rollback.
3. Telegram Dashboard v2.
4. Documentation + README rebuild.
5. Website v2.
6. Full acceptance and release.

Critical correctness fixes can be published earlier as `v1.1.x` patches.

## Definition of done

A stable release is not only “RDP connects”. It means:

```text
fresh install works
multiple PCs work
status is truthful
OFF really closes access
ON really restores access
RESTART is deterministic
DELETE revokes access
reboots recover automatically
network loss recovers automatically
updates rollback safely
CI passes
README/docs/site all describe the same actual product
```
