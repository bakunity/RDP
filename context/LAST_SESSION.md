# Hermes RDP — Last Session Handoff

Updated: 2026-08-07

This file is the compact delta from the latest long ChatGPT session. It is intentionally shorter than `PROJECT_HANDOFF.md` and should be read immediately after `context/README.md`.

## What was just confirmed in real use

The OpenSSH-based Hermes RDP path is working end-to-end.

Confirmed by the user on a real Windows PC:

- Windows installer completed successfully after using a valid fresh pairing code;
- external RDP connection works through the Hermes server;
- Windows was rebooted and, after startup/reconnect delay, RDP became available again automatically;
- pressing **OFF** in Telegram broke the active RDP session;
- pressing **ON** allowed the RDP session to connect again;
- the user explicitly confirmed that the ON/OFF functionality works.

Evidence classification:

```text
Windows reboot -> automatic client/tunnel recovery -> PASS
OFF -> active RDP session becomes unusable/disconnects -> PASS
ON -> RDP access becomes usable again -> PASS
```

Important nuance: the server endpoint was not separately probed with a port check during the OFF state in the final test, so `OFF -> endpoint CLOSED` should not yet be promoted to a separate low-level network PASS solely from this session. The user-visible access behavior is confirmed.

## Pairing UX observation

One install attempt returned a pairing-code-expired error. This was not an architecture failure; the short-lived pairing code had expired. A fresh pairing flow subsequently completed successfully.

Future UI/installer work should make an expired pairing code obvious and easy to retry without producing a confusing wall of PowerShell error output.

## What is no longer the main question

Do not spend the next chat proving whether OpenSSH reverse RDP works at all. It does.

The project has already passed:

- clean OpenSSH client installation;
- real external RDP;
- reboot recovery on the tested Windows PC;
- user-visible OFF/ON behavior.

The remaining work is product stabilization and truthful observability.

## Main unresolved issue from the last analysis

Telegram can still show contradictory transport telemetry, for example:

```text
Agent: ONLINE
SSH tunnel: stopped
Endpoint/RDP: actually usable
```

This means the next engineering target is **state correctness**, not another transport migration.

Likely telemetry mismatch to verify:

- the Windows agent's SSH-process detector is stricter than the installer's post-install SSH-process check;
- the actual `ssh.exe` may be running correctly while the telemetry matcher fails to recognize it;
- orphan/legacy SSH processes should also be ruled out.

Do not mark that root cause confirmed until the real Windows `ssh.exe` command line is inspected.

## Correct state model to implement

Keep these independent:

```text
Agent heartbeat     ONLINE / OFFLINE
Desired access      ENABLED / DISABLED
Command lifecycle   PENDING / SUCCESS / FAILED / TIMEOUT
SSH transport       CONNECTED / DISCONNECTED / UNKNOWN
Public endpoint     OPEN / CLOSED / UNKNOWN
RDP sessions        N
```

A valid disabled device can be:

```text
Agent ONLINE
Access DISABLED
SSH DISCONNECTED
Endpoint CLOSED
```

The agent must remain ONLINE while access is disabled so it can receive the next ON command.

## Recommended immediate next step

Before redesigning the website or adding unrelated features:

1. inspect the actual Hermes `ssh.exe` process/command line on the tested Windows PC;
2. compare it with the agent's `Get-SshProcesses` matching logic;
3. make measured SSH/endpoint state truthful;
4. expose command completion/result in Telegram instead of only “command sent”;
5. then implement Dashboard v2 on top of the corrected state model.

After state correctness, continue the remaining reliability matrix: network-loss recovery, server reboot, controller/sshd restart, multi-device isolation, DELETE/revoke, safe port reuse, update/rollback.

## Current product vector

Hermes RDP is a self-hosted multi-PC remote-access control plane:

```text
Windows PCs -> one public Linux Hermes server -> standard RDP clients
                         |
                         +-> Telegram pairing, control, telemetry
```

OpenSSH is the transport implementation, not the product identity.

## Working rules for the next chat

- Read the rest of `context/` before modifying code.
- Verify current GitHub `main`, release and relevant branches/PRs.
- Do not reintroduce FRP.
- Do not disable Microsoft Defender as an installation strategy.
- Do not retest already-confirmed basics unless a code change could have regressed them.
- During live infrastructure work, use one stage at a time and verify output before continuing.
- Prefer copy-paste commands; avoid requiring manual `nano`/`vim` edits.
- Never put secrets, pairing codes, tokens, private keys, Telegram numeric IDs or unnecessary production IPs into context files.
