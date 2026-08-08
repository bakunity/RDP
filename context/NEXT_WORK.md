# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-08

For the exact current step read `ACTIVE_WORK.md`. This file is the product-level work queue and should be refreshed whenever stages materially move.

## North-star goal

Ship a stable self-hosted product where a user can:

1. install Hermes on a clean Debian/Ubuntu server;
2. add supported Windows/Windows Server machines through Telegram;
3. paste one generated command into elevated PowerShell;
4. get a persistent endpoint per device;
5. connect through standard Microsoft Remote Desktop from another network;
6. trust every Telegram status;
7. survive reboots/network interruptions automatically;
8. update safely without losing access;
9. understand the system from coherent documentation.

## Already confirmed — do not redo without a regression reason

```text
OpenSSH reverse RDP baseline                     PASS
External RDP over another network                PASS
Windows reboot -> access recovers                PASS
Telegram OFF -> active RDP interrupted           PASS
Telegram ON -> RDP restored                      PASS
OFF -> server endpoint measured CLOSED           PASS
ON -> server endpoint measured OPEN              PASS
Direct LAN/VPN RDP classification                PASS
Hermes RDP classification                        PASS
Existing-install safety guard                    PASS
Win10 x86 PowerShell -> Sysnative native probe   PASS
```

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

Active implementation lives in PR #19 (`fix/control-state-dashboard`).

## Stage 1 — finish PR #19 acceptance

### 1. Telemetry performance

Implemented, still live-test:

```text
FAST ~3s
heartbeat + commands + access + SSH + RDP channel

BACKGROUND ~15s
CPU + RAM + disk + network + sessions + route + uptime

OBSERVE 60s
resources ~3s
TOP processes ~6s
Telegram refresh ~3s
auto-off after 60s
```

Acceptance:

- deploy latest server-side branch state with backup;
- update MIPC agent preserving identity/key/port;
- measure timing again;
- verify RDP micro-freezes disappear or materially reduce;
- verify `НАБЛЮДАТЬ 60с` enables heavy telemetry;
- verify automatic stop after 60 seconds and no endless Telegram live redraw.

### 2. Windows Server installer

Confirmed old bug: blanket `ProductType != 1` rejection.

Fix exists for ProductType 2/3.

Acceptance:

- real fresh Windows Server installation;
- task/tunnel/endpoint come online;
- RDP works through assigned endpoint;
- no client-only rejection remains.

### 3. Win10 x64 + x86 PowerShell final acceptance

Resolver/runtime behavior is already proven.

Still required:

- genuinely fresh patched install launched from x86 PowerShell on x64 Win10;
- Microsoft system OpenSSH chosen without PATH/Git fallback;
- keys/task/tunnel/endpoint complete successfully.

### Merge gate

Do not merge PR #19 until the three acceptance groups above are complete or consciously split into a follow-up PR with explicit evidence boundaries.

## Stage 2 — recovery / lifecycle matrix

After PR #19:

- RESTART actually recreates/reconnects transport;
- temporary Windows network loss -> reconnect;
- Linux server reboot -> controller + dedicated sshd recover -> clients reconnect;
- controller restart;
- dedicated sshd restart;
- repeated reconnect without duplicate/orphan Hermes SSH processes;
- two+ devices simultaneously;
- one device failure does not affect another.

Windows reboot baseline is already PASS.

## Stage 3 — device/security lifecycle

Verify formally:

- unique Ed25519 identity per device;
- first device key cannot claim second endpoint;
- private key never reaches server;
- revoked key cannot authenticate;
- DELETE revokes API token and SSH key;
- DELETE closes endpoint;
- freed port is safely reusable only after cleanup;
- administrative SSH stays independent;
- Telegram authorization remains owner-limited;
- no Defender exclusions are required.

## Stage 4 — safe migration / update / rollback

### Legacy Windows migration

Replace fragile recursive backup of protected legacy directories with whole-directory archival/rename and scoped ACL fallback only when needed.

### Server updater target

```text
backup
 -> stage
 -> checks
 -> restart
 -> health checks
 -> reconnect/endpoint smoke test
 -> commit

failure
 -> automatic rollback
 -> restart previous version
 -> verify previous health
```

### Windows client updater target

```text
backup current agent/config state
 -> stage new agent
 -> parse/start checks
 -> heartbeat/tunnel health check
 -> keep update

failure
 -> restore previous agent
 -> restart task
 -> verify previous access
```

## Stage 5 — command timeout / UX polish

Current branch has stronger command lifecycle/pending/result semantics. Remaining polish:

- deterministic command timeout;
- concise pairing-code-expired UX;
- clear repair/update flow instead of abusing `Добавить ПК`;
- confirm Russian dashboard terminology after live deployment.

## Stage 6 — documentation rebuild

After behavior stabilizes:

- restore rich architecture diagrams and lifecycle explanations;
- use v1.0.7 only as structural inspiration, never restore FRP implementation details;
- document server/client responsibilities, pairing, ON/OFF/RESTART, state model, trust chain, failure/recovery and multi-device isolation;
- sweep stale FRP/version claims;
- restore polished README structure/badges/links.

Core statement:

> All Windows devices are equal clients. Only the Hermes Linux server has a special infrastructure role.

## Stage 7 — Website v2

Explain product first:

```text
Windows devices -> one Hermes server -> standard RDP clients
                         |
                         -> Telegram control
```

Then explain OpenSSH, per-device Ed25519 isolation, pinning, persistent endpoints and telemetry.

## Stage 8 — final acceptance / release

Before publishing v1.2.0:

- all release-facing fixes moved from `IMPLEMENTED, NOT VALIDATED` to PASS or explicitly excluded;
- release draft reconciled with `EVIDENCE_LEDGER.md`;
- `CURRENT_STATE.md` and `ACTIVE_WORK.md` updated;
- docs/README consistent with actual runtime;
- published tag immutable;
- rollback/recovery story documented.

## Context discipline during all stages

Do not wait for chat migration.

After meaningful work-units:

- update `ACTIVE_WORK.md`;
- update `EVIDENCE_LEDGER.md` for real evidence;
- update release draft for release-facing changes;
- refresh this work queue when priorities materially change.