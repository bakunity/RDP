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

## Windows 10 x64 + 32-bit PowerShell installer compatibility bug

A separate real Windows 10 Pro x64 machine exposed a confirmed installer bug.

Observed environment:

```text
Windows 10 Pro x64
Build 19045
Is64BitOS      = True
Is64BitProcess = False
PowerShell     = C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe
OpenSSH.Client = Installed
RebootPending  = False
```

The current Hermes Windows installer assumes the Microsoft OpenSSH binaries are reachable only through:

```text
C:\Windows\System32\OpenSSH\ssh.exe
C:\Windows\System32\OpenSSH\ssh-keygen.exe
```

From a 32-bit PowerShell process on 64-bit Windows, filesystem redirection means that direct `System32` lookup does not reach the native 64-bit system directory as intended. The real Microsoft OpenSSH binaries are visible through the native alias:

```text
C:\Windows\Sysnative\OpenSSH\ssh.exe
C:\Windows\Sysnative\OpenSSH\ssh-keygen.exe
```

This root cause is considered **CONFIRMED** for that failed install scenario.

Important: `Get-Command ssh.exe` on that PC can resolve to Git's bundled SSH. Hermes must **not** fix this by using PATH or the first `ssh.exe` found. The product requires the Windows system Microsoft OpenSSH implementation.

Required compatibility logic:

```powershell
if ([Environment]::Is64BitOperatingSystem -and -not [Environment]::Is64BitProcess) {
    $NativeSystem = "$env:WINDIR\Sysnative"
} else {
    $NativeSystem = "$env:WINDIR\System32"
}
```

Then resolve:

```text
$NativeSystem\OpenSSH\ssh.exe
$NativeSystem\OpenSSH\ssh-keygen.exe
```

Installer behavior should distinguish:

```text
OpenSSH installed + native binaries found      -> continue
OpenSSH not installed                          -> install, then re-check
OpenSSH installed but native binaries missing  -> clear diagnostic failure
32-bit PowerShell on x64 Windows               -> automatically use Sysnative
```

Do not require users to manually launch the “correct” PowerShell as the permanent product solution. Do not use Git SSH/PATH fallback.

Temporary test workaround used during diagnosis: launch native 64-bit PowerShell through `Sysnative` and rerun installation. Pairing occurs after OpenSSH resolution, so this specific pre-pair failure should not consume a pairing code; an expired code may still need regeneration because of normal time expiry.

This is now a concrete `v1.2.0` stabilization item:

> **Windows compatibility layer: x86 PowerShell -> x64 Windows Microsoft OpenSSH resolution.**

## Pairing UX observation

One install attempt returned a pairing-code-expired error. This was not an architecture failure; the short-lived pairing code had expired. A fresh pairing flow subsequently completed successfully.

Future UI/installer work should make an expired pairing code obvious and easy to retry without producing a confusing wall of PowerShell error output.

## What is no longer the main question

Do not spend the next chat proving whether OpenSSH reverse RDP works at all. It does.

The project has already passed:

- clean OpenSSH client installation on the tested normal path;
- real external RDP;
- reboot recovery on the tested Windows PC;
- user-visible OFF/ON behavior.

The Windows 10 x86-PowerShell issue is an installer compatibility defect, not evidence that the OpenSSH transport architecture is wrong.

The remaining work is product stabilization, Windows compatibility and truthful observability.

## Main unresolved issue from the last analysis

Telegram can still show contradictory transport telemetry, for example:

```text
Agent: ONLINE
SSH tunnel: stopped
Endpoint/RDP: actually usable
```

This means the next control-plane engineering target is **state correctness**, not another transport migration.

Likely telemetry mismatch to verify:

- the Windows agent's SSH-process detector is stricter than the installer's post-install SSH-process check;
- the actual `ssh.exe` may be running correctly while the telemetry matcher fails to recognize it;
- orphan/legacy SSH processes should also be ruled out.

Do not mark that telemetry root cause confirmed until the real Windows `ssh.exe` command line is inspected.

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

## Recommended immediate next steps

Before redesigning the website or adding unrelated features:

1. fix Windows native OpenSSH path resolution for x86 PowerShell on x64 Windows and add regression coverage;
2. inspect the actual Hermes `ssh.exe` process/command line on the tested Windows PC;
3. compare it with the agent's `Get-SshProcesses` matching logic;
4. make measured SSH/endpoint state truthful;
5. expose command completion/result in Telegram instead of only “command sent”;
6. then implement Dashboard v2 on top of the corrected state model.

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
- Do not use arbitrary PATH/Git SSH as a fallback for system Microsoft OpenSSH.
- Do not require 64-bit PowerShell as a user workaround once the installer compatibility fix is implemented.
- Do not retest already-confirmed basics unless a code change could have regressed them.
- During live infrastructure work, use one stage at a time and verify output before continuing.
- Prefer copy-paste commands; avoid requiring manual `nano`/`vim` edits.
- Never put secrets, pairing codes, tokens, private keys, Telegram numeric IDs or unnecessary production IPs into context files.
