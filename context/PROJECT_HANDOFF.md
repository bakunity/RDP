# Hermes RDP — Project Handoff

Updated: 2026-08-08

Purpose: stable architecture/product context. For current PR/deployment/blockers read `ACTIVE_WORK.md`; for proven behavior read `EVIDENCE_LEDGER.md`; for current product snapshot read `CURRENT_STATE.md`.

## Product vector

Hermes RDP is a self-hosted **multi-device remote-access control plane**:

> One public Linux Hermes server provides controlled RDP access to multiple Windows devices. Every device has its own persistent endpoint and identity; Telegram provides pairing, status and access control.

OpenSSH is the transport implementation, not the product identity.

## Architecture

```text
Telegram user
     |
     v
Hermes Controller / HTTPS API / SQLite
     |
     +---- dedicated Hermes sshd
                 |
          reverse OpenSSH
           /      |      \
      Windows   Windows   Windows
       :3389     :3389     :3389
           \      |      /
        persistent per-device
          public RDP endpoints
                 |
          standard RDP client
```

### Linux server

- `hermes-rdp.service`: HTTPS API + Telegram bot + SQLite registry;
- `hermes-rdp-sshd.service`: isolated OpenSSH daemon for reverse forwarding;
- administrative SSH remains separate;
- server allocates a persistent public RDP endpoint per device;
- server stores device public keys and enforces endpoint isolation.

### Windows device

- Microsoft system `ssh.exe` / `ssh-keygen.exe`;
- `HermesRdpAgent.ps1` runs as Scheduled Task under `SYSTEM`;
- per-device Ed25519 keypair;
- per-device API token / device ID / assigned RDP port;
- private SSH key stays on Windows;
- API certificate is pinned;
- SSH host key is received through the pinned HTTPS API and stored in dedicated `known_hosts`.

## Durable boundaries

### All Windows devices are equal clients

There is no “main PC” architecture. A desktop, laptop or Windows Server follows the same device model unless a platform-specific compatibility path is explicitly required.

Only the Linux Hermes server has the infrastructure role.

### OpenSSH replaced FRP

FRP was removed from the active runtime after the Windows deployment experience conflicted with Microsoft Defender. Do not reintroduce FRP as a casual workaround.

### Do not weaken Defender

The supported product path must not depend on disabling Defender or adding broad exclusions.

### Telegram is control plane only

RDP traffic does not pass through Telegram.

### Agent online is independent from access enabled

A valid disabled state is:

```text
Agent online
Desired access off
Applied access off
SSH disconnected
Public endpoint closed
```

The agent remains online so it can receive the next ON command.

### Dashboard represents measured truth

Keep independent concepts for:

- agent heartbeat;
- desired RDP access;
- applied agent access state;
- command lifecycle/result;
- SSH transport/process state;
- server endpoint listener state;
- actual RDP-channel activity.

Do not infer one dimension solely from another.

### Per-device trust/isolation

Each device owns its own identity. The private key never goes to the server. The server-side SSH authorization must restrict a device to its assigned endpoint.

### Stable releases use immutable refs

Published tags are immutable. Production installation/update documentation should use a release tag or known immutable commit, not mutable `main`.

## Proven product baseline

The detailed acceptance matrix is in `EVIDENCE_LEDGER.md`. Stable high-level baseline includes:

- OpenSSH reverse RDP works end-to-end;
- real external-network RDP works;
- tested Windows reboot recovery works;
- Telegram OFF/ON works at user-visible level;
- server-authoritative public endpoint CLOSED/OPEN has been live-validated on the stabilization branch;
- direct LAN/VPN RDP vs Hermes RDP channel classification has been live-validated;
- existing-install safety guard has been live-validated;
- native OpenSSH visibility through `Sysnative` under x86 PowerShell on x64 Win10 is confirmed.

Do not re-prove these baselines unless a relevant change can regress them.

## Product phase

Current broad phase: **stabilization** toward `v1.2.0`.

The project should prioritize:

1. deterministic installation/compatibility;
2. truthful low-cost telemetry/control;
3. recovery and lifecycle acceptance;
4. safe migration/update/rollback;
5. coherent Telegram UX;
6. documentation/README rebuild;
7. Website v2;
8. final release acceptance.

Exact current order and blockers belong in `ACTIVE_WORK.md` / `NEXT_WORK.md`, not here.

## Known future product areas

These are broad areas, not a current TODO checklist:

- reconnect/recovery under network/server/service failures;
- device revoke/delete/port reuse/isolation acceptance;
- legacy Windows protected-ACL migration;
- transactional server/client update + rollback;
- command timeout semantics;
- rich explanatory docs/README;
- final Website v2.

Use `NEXT_WORK.md` for actual remaining queue because individual items may already have moved to PASS.

## Documentation/product presentation principles

Documentation should explain the system visually and behaviorally, not just list files.

Core user-facing model:

```text
Windows devices -> one Hermes server -> Remote Desktop from anywhere
                         |
                         +-> Telegram control
```

Explain the product first, then OpenSSH/Ed25519/pinning implementation details.

Older `v1.0.7` documentation may be used as a structural/clarity reference only; do not restore obsolete FRP implementation details.

## Engineering interaction rules

- Russian;
- direct practical engineering discussion;
- one live infrastructure stage at a time;
- whole copy-paste commands instead of manual editor workflows where possible;
- explicit PASS/FAIL from evidence;
- rollback plan/point for risky changes where practical;
- do not expose secrets in diagnostics/context;
- do not claim deployed/current state from code alone;
- do not let chat be the only copy of durable project facts.

## Context note

This file intentionally avoids active PR SHA, temporary root-cause hypotheses and detailed open acceptance. Those facts change quickly and belong to HOT context.

If this file starts accumulating temporary debugging state again, compact it according to `CONTEXT_LIFECYCLE.md`.