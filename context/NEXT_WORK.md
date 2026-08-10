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

PR #19 is merged. Reconciled CI #175 passed. Current `main` contains the accepted stabilization product code.

## Stage 2 — recovery / lifecycle matrix — ACTIVE

Run one scenario at a time and record PASS/FAIL evidence.

Completed and removed from the active queue:

- **RL-001 Telegram RESTART — PASS**: old Hermes SSH PID replaced, one healthy tunnel returned, access stayed ON, endpoint returned OPEN, active RDP recovered after the short interruption.
- **RL-002 temporary Windows-side network loss — PASS**: agent automatically recreated one Hermes SSH transport with no Telegram command; RDP worked again after recovery. The intentionally long outage exceeded Microsoft RDP's client retry window.
- **RL-003 Linux server reboot — PASS**: real reboot restored server services, Telegram/dashboard, Windows reverse tunnel and the already-open RDP session automatically.
- **RL-004 controller restart — PASS**: controller PID changed while dedicated sshd PID and active endpoint session PID stayed unchanged; listeners remained available, Telegram/dashboard worked, and RDP had no interruption.
- **RL-005 dedicated Hermes sshd restart — PASS**: controller stayed untouched; dedicated sshd and endpoint session were replaced; Windows automatically recreated the reverse tunnel; the same public endpoint returned; Telegram/dashboard stayed healthy; and the already-open RDP session recovered automatically.

Current queue:

1. **Repeated reconnects -> no duplicate/orphan Hermes SSH processes.**
2. Two+ devices simultaneously remain healthy.
3. Failure of one device does not affect another.

Windows reboot recovery is already PASS and is not repeated without a regression reason.

For RL-006, use a bounded repeated-reconnect smoke rather than a prolonged outage. Recreate the dedicated transport several times, waiting for the tested endpoint to return after each cycle. Acceptance: every cycle returns exactly one endpoint session; no stale session/listener accumulates; Windows ends with exactly one Hermes `ssh.exe`; access remains enabled; controller and Telegram/dashboard remain healthy; and RDP remains usable after the sequence. Whether the already-open RDP client visually reconnects on every individual cycle is useful observation but not the primary RL-006 gate.

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

- architecture diagrams and lifecycle explanations;
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

Optional after lifecycle work: lightweight context-hygiene/lint checks for required files, freshness, size and obvious contradictory status patterns.
