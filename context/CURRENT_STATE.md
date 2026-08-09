# Hermes RDP — Current State Snapshot

Updated: 2026-08-09

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Active stabilization PR: **#19**, branch `fix/control-state-dashboard`.
- Current PR head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- Target release: **v1.2.0 — Stabilization**.
- Product changes from PR #19 are not merged to `main` yet.
- Context-only commits continue to advance `main`; feature branch must be reconciled with current base + CI before merge.

## Architecture — current

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent public endpoint per device
```

Durable boundaries:

- all Windows devices are equal clients;
- only Linux Hermes server is infrastructure-special;
- admin SSH remains independent;
- FRP is not active runtime transport;
- private per-device SSH key stays on Windows;
- server restricts public key to the assigned endpoint;
- Telegram is control plane, not RDP transport;
- agent heartbeat continues while RDP access is OFF.

## Deployment truth

Server is live on immutable head:

`586e9446ea41262f1ed0d9c84ba72838a47d9bc5`

MIPC Windows agent is live on immutable head:

`c51ed8fa2c090dbc731a0c06f357d899846e90ae`

The split is intentional: changes after `586e944...` in the active PR are Windows-agent/test only, so no Linux redeploy was required.

Current-head MIPC update preserved device ID, assigned RDP port, config and private key; Scheduled Task remained Running and exactly one Hermes `ssh.exe` was present immediately after update. The installed agent contains the .NET TCP fast path, 15-second SSH PID cache and loopback peer helper, with the old executable `Get-NetTCPConnection` RDP path removed.

## Stable accepted baseline

Real testing has confirmed on accepted builds:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- Windows reboot -> automatic Hermes recovery -> RDP usable;
- Telegram OFF interrupts access and ON restores it;
- OFF can correctly remain `agent online + desired/applied off + SSH disconnected + endpoint closed`;
- Linux server listener authoritatively reports assigned endpoint CLOSED/OPEN;
- existing-install guard preserves working identity/key/port;
- Win10 x64 under x86 PowerShell reaches native Microsoft OpenSSH through `Sysnative`.

Do not re-run these wholesale without a concrete regression reason.

## Performance stabilization — accepted for current working path

The original micro-freeze regression was traced to expensive work inside the old 3-second agent loop, including NetTCPIP and WMI queries.

Current PR separates work into:

```text
FAST ~3s
heartbeat + commands + access + cached SSH state + lightweight RDP classification

BACKGROUND ~15s
CPU + RAM + disk + network + sessions + route + uptime

OBSERVE 60s
resources ~3s
TOP processes ~6s
Telegram render ~3s
then automatic stop
```

Live current-head timing on MIPC:

```text
SSH cached PID        avg 21.63 ms, max 73.51 ms
.NET RDP snapshot     avg 19.68 ms, max 71.04 ms
FAST core combined    avg 27.46 ms, max 43.69 ms
SSH full refresh      avg 312.72 ms, max 401.56 ms
```

The full SSH WMI refresh is periodic rather than ordinary per-cycle work.

Subjective acceptance on the current working Hermes path is now **PASS**: user reports smooth normal work, no noticeable lag/micro-freezes, and clear improvement over the previous build. Direct RDP inside the local network still feels somewhat more immediate, but Hermes RDP is accepted as good for normal work. No noticeable ~15-second periodic stall was reported during the acceptance window.

Performance regression status: **RESOLVED FOR THE CURRENT TESTED WORKING PATH**.

## Network/routing finding

A temporary host-specific route bypassed Karing and proved real direct Wi-Fi RTT to Hermes around 85–95 ms. However, after recreating the reverse SSH tunnel on that direct route, subjective RDP became materially worse and the Windows RDP quality indicator dropped.

Therefore Karing cannot currently be treated as the sole/main cause of steady-state RDP lag, and direct routing is not automatically better in this environment. The accepted current working path should remain the baseline while regression smoke continues.

## RDP channel classification — current-head smoke still required

Pre-optimization live acceptance proved:

```text
direct LAN/VPN RDP  -> Hermes=0, direct=1
Hermes RDP          -> Hermes=1, direct=0
open endpoint alone -> Hermes=0
```

The newest agent changed implementation to .NET TCP snapshots plus conditional loopback peer correlation. Historical classification remains valid baseline evidence, but current head still needs explicit smoke for:

- **RV-002:** active Hermes RDP -> `Hermes=1/direct=0`;
- **RV-003:** endpoint/tunnel open with no Hermes client -> `Hermes=0`;
- **RV-001:** direct LAN/VPN RDP -> `Hermes=0/direct=1`.

## Control/current-head smoke still required

Because process-cache/main-loop behavior changed, also revalidate:

- **RV-004/RV-006:** OFF -> applied OFF + endpoint CLOSED; ON -> one tunnel + endpoint OPEN;
- **RV-005:** exactly one Hermes `ssh.exe` in normal ON state.

## Windows compatibility

### Win10 x64 + x86 PowerShell

Confirmed runtime behavior:

- 64-bit Windows;
- 32-bit PowerShell under `SysWOW64`;
- direct `System32` view redirected;
- `Sysnative` reaches native Microsoft OpenSSH;
- no PATH/Git-SSH fallback should be used.

PR #19 implements native resolution and stores canonical `System32` SSH path in config.

Status:

- Sysnative runtime/probe behavior — **PASS**;
- existing-install guard — **PASS**;
- genuinely fresh full patched install launched from x86 PowerShell — **IMPLEMENTED, NOT VALIDATED**.

### Windows Server

Confirmed old bug: installer blocked `ProductType != 1` before its later Server edition check.

Current PR allows ProductType 2/3 with regression coverage.

Status: **IMPLEMENTED, NOT LIVE VALIDATED**. Real fresh Windows Server install is required.

## CI

Current PR head `c51ed8fa...` has green CI (#139), including Linux release checks and Windows PowerShell 5.1 parse/certificate pinning.

CI proves source/static checks, not remaining live acceptance scenarios.

## Immediate blockers before PR #19 merge

1. targeted current-head smoke RV-001..RV-006, one scenario at a time;
2. `НАБЛЮДАТЬ 60с` + automatic stop acceptance;
3. real Windows Server fresh install;
4. fresh Win10 x64/x86-PowerShell full install;
5. reconcile feature branch with advanced `main`, rerun CI, recheck mergeability;
6. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

Exact current order is maintained in `ACTIVE_WORK.md` / `NEXT_WORK.md`.