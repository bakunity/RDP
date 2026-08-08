# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-08

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

## Stable baseline — do not re-prove wholesale

The following have real baseline evidence:

- OpenSSH reverse RDP architecture works;
- external-network RDP works;
- tested Windows reboot recovery works;
- Telegram OFF/ON works on the previously accepted build;
- server endpoint CLOSED/OFF + OPEN/ON works on the previously accepted stabilization build;
- direct vs Hermes RDP classification works on the pre-optimization classifier;
- existing-install guard works;
- Win10 x86 PowerShell can reach native Microsoft OpenSSH through `Sysnative`.

Important evidence rule: the newest low-cost telemetry/main-loop refactor touches RDP classification, SSH process detection and command polling. Therefore **targeted current-head smoke is required for those touched paths**. This is not a request to repeat the whole historical acceptance matrix.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

Active implementation: PR #19, `fix/control-state-dashboard`.

## Stage 1 — finish PR #19 acceptance

### A. Immutable current-head deployment

For acceptance, deploy/update using the exact PR head SHA rather than mutable branch name so server and Windows agent provenance is known.

Current acceptance head at this checkpoint:

```text
586e9446ea41262f1ed0d9c84ba72838a47d9bc5
```

Future updater reliability work should resolve/store/print deployed commit SHA automatically; current updater only stores the supplied ref.

### B. Telemetry performance

Implemented model:

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

- update MIPC preserving identity/key/port;
- re-measure cost;
- verify RDP micro-freezes disappear or materially reduce;
- verify background resource cadence;
- verify explicit observation enables detailed telemetry;
- verify observation/3s redraw stops automatically after 60s.

### C. Targeted current-head regression smoke

Because the optimization changed previously accepted paths, verify on the new agent:

- one Hermes `ssh.exe` in normal ON state;
- OFF still applies and closes endpoint;
- ON restores exactly one tunnel and opens endpoint;
- direct LAN/VPN RDP -> Hermes=0/direct=1;
- Hermes RDP -> Hermes=1/direct=0;
- open endpoint with no Hermes RDP client -> Hermes=0.

No need to re-run unrelated external-RDP/reboot/Sysnative baseline tests here.

### D. Windows Server installer

Confirmed old bug: client-only `ProductType != 1` rejection.

Fix supports ProductType 2/3 with regression coverage.

Acceptance:

- real fresh Windows Server install from the same immutable head;
- task/tunnel/endpoint online;
- assigned RDP endpoint usable;
- no old client-only rejection.

### E. Win10 x64 + x86 PowerShell final e2e

Runtime `Sysnative` resolver behavior is already proven.

Still required:

- genuinely fresh patched installation launched from x86 PowerShell on x64 Win10;
- Microsoft system OpenSSH selected without PATH/Git fallback;
- key/task/tunnel/endpoint complete successfully.

### F. PR merge preparation

Continuous context-only commits advanced `main` while PR #19 stayed on its older base.

Before merge:

- reconcile current `main` into/rebase feature branch;
- resolve actual conflicts if any;
- rerun CI after reconciliation;
- recheck mergeability;
- do not interpret simple base drift as a product failure.

### PR #19 merge gate

Merge only when A–F are accepted, or consciously split a remaining scenario into a follow-up with explicit evidence boundary.

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

The updater currently does **not** resolve/print/store exact downloaded commit when given a mutable branch ref; fix this in this stage.

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

The durable memory architecture is now designed for continuous checkpoint + compaction. One optional future improvement remains: a lightweight automated context-hygiene/lint check (required files, freshness headers/links, size warnings, obvious contradictory status patterns). Do this only after PR #19 merge/reconciliation so context tooling does not further complicate the active feature-branch base drift.