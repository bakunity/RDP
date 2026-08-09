# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-10

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can:

1. install Hermes on a clean Debian/Ubuntu server;
2. add supported Windows / Windows Server devices through Telegram;
3. paste one generated elevated-PowerShell command;
4. receive a persistent per-device endpoint;
5. connect with standard Microsoft Remote Desktop from another network;
6. trust every Telegram status;
7. survive reboots/network interruptions automatically;
8. update safely without losing access;
9. operate the system from coherent documentation.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

Active implementation: PR #19, `fix/control-state-dashboard`, current head `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.

## Stage 1 — finish PR #19 acceptance

Already accepted and removed from the active test queue:

- immutable MIPC update with identity/key/port preservation;
- fast-path timing and subjective performance;
- RV-001..RV-006 current-head regression smoke;
- `НАБЛЮДАТЬ 60с` including automatic stop;
- full Windows Server 2019 ProductType=3 acceptance: clean install, current-head agent update preserving identity/key/port/config, one Hermes SSH process and successful real RDP connection through the assigned endpoint.

### A. Win10 x64 + x86 PowerShell final e2e

Runtime `Sysnative` resolver behavior is already proven.

Still required:

- genuinely fresh patched installation launched from x86 PowerShell on x64 Win10;
- Microsoft system OpenSSH selected without PATH/Git fallback;
- key/task/tunnel/endpoint complete successfully;
- real RDP connection through the assigned endpoint.

Do not repeat the standalone Sysnative probe unless the fresh-install result contradicts it.

### B. PR merge preparation

Continuous context-only commits advanced `main` while PR #19 stayed on its older base.

Before merge:

- reconcile current `main` into/rebase feature branch;
- resolve actual conflicts if any;
- rerun CI after reconciliation;
- recheck mergeability;
- do not interpret simple base drift as a product failure.

### PR #19 merge gate

Merge only when A–B are accepted, or consciously split a remaining scenario into a follow-up with explicit evidence boundary.

## Stage 2 — recovery / lifecycle matrix

After PR #19:

- RESTART really recreates/reconnects transport;
- temporary Windows network loss -> reconnect;
- Linux server reboot -> controller + dedicated sshd recover -> clients reconnect;
- controller restart;
- dedicated sshd restart;
- repeated reconnect without duplicate/orphan Hermes SSH;
- two+ devices simultaneously;
- one device failure does not affect another.

Windows reboot baseline is already PASS.

## Stage 3 — device/security lifecycle

Verify formally:

- unique Ed25519 identity per device;
- first device key cannot claim second endpoint;
- private key never reaches server;
- revoked key cannot authenticate;
- DELETE revokes API token + SSH key;
- DELETE closes endpoint;
- freed port reused only after safe cleanup;
- admin SSH remains independent;
- Telegram authorization remains owner-limited;
- no Defender exclusions required.

## Stage 4 — safe migration / updater / rollback

### Legacy Windows migration

Replace fragile recursive protected-directory backup with whole-directory archival/rename and scoped ACL fallback only when necessary.

### Server updater

Target contract:

```text
resolve immutable source SHA
 -> backup
 -> stage
 -> syntax/config checks
 -> restart
 -> health checks
 -> reconnect/endpoint smoke
 -> record deployed SHA
 -> commit

failure
 -> automatic rollback
 -> restart previous version
 -> verify previous health
```

Current updater still does not resolve/print/store exact downloaded commit when given a mutable branch ref.

### Windows client updater

Target:

```text
backup agent/config identity
 -> stage new agent
 -> parse/start checks
 -> heartbeat/tunnel health
 -> keep update

failure
 -> restore previous agent
 -> restart task
 -> verify previous access
```

## Stage 5 — command / pairing / repair UX

- deterministic command timeout;
- concise expired-pairing-code retry UX;
- explicit repair/update flow instead of abusing `Добавить ПК`;
- finalize Russian dashboard terminology after latest live deployment.

## Stage 6 — documentation rebuild

After behavior stabilizes:

- rich architecture diagrams and lifecycle explanations;
- server/client responsibilities;
- pairing, ON/OFF/RESTART and state model;
- trust chain and multi-device isolation;
- failure/recovery/update behavior;
- stale FRP/version sweep;
- polished README structure/badges/links.

Core statement:

> All Windows devices are equal clients. Only the Hermes Linux server has a special infrastructure role.

## Stage 7 — Website v2

Explain product first:

```text
Windows devices -> one Hermes server -> standard RDP clients
                         |
                         -> Telegram control
```

Then OpenSSH, Ed25519 isolation, pinning, persistent endpoints and telemetry.

## Stage 8 — final v1.2.0 acceptance / release

Before release:

- release-facing items are PASS or explicitly excluded;
- release draft reconciled with evidence ledger;
- release evidence snapshot archived;
- `ACTIVE_WORK/CURRENT_STATE/NEXT_WORK` compacted to released truth/next cycle;
- superseded context retired;
- docs/README match actual runtime;
- published tag immutable;
- rollback/recovery story documented.

## Context-system follow-up

Optional after PR #19 merge/reconciliation: lightweight context-hygiene/lint checks for required files, freshness, size and obvious contradictory status patterns.