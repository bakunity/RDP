# Hermes RDP — Current State Snapshot

Updated: 2026-08-08

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Active stabilization PR: **#19**, branch `fix/control-state-dashboard`.
- Current PR head at this snapshot: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Target release: **v1.2.0 — Stabilization**.
- Product changes from PR #19 are not merged to `main` yet.
- Context-only commits have advanced `main`; feature branch must be reconciled with current base + CI before merge.

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
- server restricts public key to assigned endpoint;
- Telegram is control plane, not RDP transport;
- agent heartbeat continues while RDP access is OFF.

## Stable live baseline

Real testing has confirmed on accepted builds:

- fresh normal-path OpenSSH Windows install;
- external-network RDP;
- Windows reboot -> automatic Hermes recovery -> RDP usable;
- Telegram OFF interrupts access and ON restores it;
- OFF can correctly remain `agent online + desired/applied off + SSH disconnected + endpoint closed`;
- Linux server listener can authoritatively report assigned endpoint CLOSED/OPEN;
- existing-install guard preserves working identity/key/port;
- Win10 x64 under x86 PowerShell reaches native Microsoft OpenSSH through `Sysnative`.

These are real facts, not hypotheses.

## State / endpoint truth

PR #19 separates:

- agent heartbeat;
- desired access;
- agent-applied access;
- SSH process/transport;
- server public listener;
- RDP channel/activity;
- pending/last command result.

The earlier contradiction `ONLINE + tunnel stopped while RDP actually works` was addressed by measured state rather than changing transport.

Public endpoint truth moved from a Windows self-probe (which could false-positive through VPN/TUN/proxy routing) to the Linux listener. Baseline live acceptance proved OFF=CLOSED and ON=OPEN.

## RDP channel classification — baseline PASS, latest-head revalidation pending

Pre-optimization live acceptance proved:

```text
direct LAN/VPN RDP -> Hermes=0, direct=1
Hermes RDP         -> Hermes=1, direct=0
open endpoint alone -> Hermes=0
```

Underlying signatures were:

- non-loopback Windows `:3389` remote address -> direct LAN/VPN;
- loopback `:3389` whose peer belongs to this device's Hermes `ssh.exe` -> Hermes.

The latest performance refactor changed `Get-RdpConnectionSummary` from a full Established-TCP scan to limited RDP/exact-peer queries. Therefore the old PASS remains valid baseline evidence but **the newest agent must revalidate these three counters** before they are claimed PASS for current head.

## Windows compatibility

### Win10 x64 + x86 PowerShell

Confirmed runtime environment/behavior:

- 64-bit Windows;
- 32-bit PowerShell under `SysWOW64`;
- direct `System32` view redirected;
- `Sysnative` reaches native Microsoft OpenSSH;
- no PATH/Git-SSH fallback should be used.

PR #19 implements native resolution and stores canonical `System32` SSH path in config.

Status:

- Sysnative runtime/probe behavior — PASS;
- existing-install guard — PASS;
- genuinely fresh full patched install launched from x86 PowerShell — **IMPLEMENTED, NOT VALIDATED**.

### Windows Server

Confirmed old bug: installer blocked `ProductType != 1` before its later Server edition check.

Current PR allows ProductType 2/3 with regression coverage.

Status: **IMPLEMENTED, NOT LIVE VALIDATED**. Real fresh Windows Server install is required.

## Performance stabilization

Before optimization on MIPC:

```text
all Established TCP connections   ~1059 ms
RDP-only TCP query                ~516 ms
full Win32_Process query          ~357 ms
TOP-process sampling window       800 ms minimum
```

The old 3-second telemetry loop could spend most of its interval collecting diagnostics, matching observed RDP micro-freezes.

Current PR implements:

```text
FAST ~3s
heartbeat + commands + access + SSH + RDP channel

BACKGROUND ~15s
CPU + RAM + disk + network + sessions + route + uptime

OBSERVE 60s
resources ~3s
TOP processes ~6s
Telegram render ~3s
then automatic stop
```

Also:

- no full Established-TCP scan for normal RDP classification;
- no background TOP-process polling;
- narrowed/reused SSH process query;
- no endless Telegram 3-second auto-render by default.

Status: **IMPLEMENTED + CI PASS, RUNTIME PERFORMANCE ACCEPTANCE PENDING**.

## Current-head targeted regression requirements

Because latest code changed agent loop/classification/process detection, revalidate:

- exactly one Hermes `ssh.exe` in normal ON state;
- OFF -> applied OFF + endpoint CLOSED;
- ON -> one tunnel + endpoint OPEN;
- direct RDP -> Hermes=0/direct=1;
- Hermes RDP -> Hermes=1/direct=0;
- endpoint open/no Hermes client -> Hermes=0.

Do not re-run unrelated historical baselines without a regression reason.

## Telegram UX on current PR

Implemented:

- Russian user-facing state vocabulary;
- separate Hermes and LAN/VPN RDP counters;
- contextual ON/OFF/RESTART controls;
- pending command state;
- `НАБЛЮДАТЬ 60с` instead of permanent LIVE 3s.

Localization/observation behavior on the latest head still belongs to current live acceptance.

## CI

PR head `586e944...` has green CI (#110) for Linux release checks, Python/static tests, PowerShell 5.1 parse and certificate pinning.

CI proves source/static checks, not Windows Server install or live performance/observation/revalidation.

## Deployment truth / provenance

A pre-latest PR build is live and passed state/endpoint/RDP-channel baseline acceptance.

The latest low-cost telemetry / observation / Windows Server head is not yet live-accepted.

Current updater accepts a supplied repository ref but does not resolve/print/store the downloaded commit SHA. Therefore upcoming acceptance should deploy the **immutable PR head SHA directly** rather than mutable branch name. Resolved deployed-SHA recording belongs to the later updater/reliability stage.

## Immediate blockers before PR #19 merge

1. immutable-head server deploy;
2. identity-preserving MIPC agent update from same SHA;
3. timing + subjective RDP performance acceptance;
4. targeted current-head regression smoke;
5. `НАБЛЮДАТЬ 60с` + auto-off acceptance;
6. real Windows Server fresh install;
7. fresh Win10 x64/x86-PowerShell e2e install;
8. reconcile feature branch with advanced `main`, rerun CI, recheck mergeability.

After PR #19, continue recovery/device lifecycle/update/rollback, then docs/README, Website v2 and final release acceptance. Exact queue is in `NEXT_WORK.md`.

## Context subsystem state

As of 2026-08-08 project memory uses:

- continuous event-driven checkpoints;
- HOT/WARM/COLD layers;
- canonical owner per fact;
- evidence scope + `REVALIDATION REQUIRED`;
- semantic staleness / `SUPERSEDED` retirement;
- release evidence rotation;
- soft size budgets / garbage collection;
- archive index;
- concurrent-writer reconciliation;
- batched checkpoint preference;
- PR/base-drift reconciliation before merge.

`LAST_SESSION.md` is not authoritative. `LATEST_AUDIT.md` is retired to a pointer until a genuinely new deep audit is needed.