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

- **RL-001 Telegram RESTART — PASS**: old Hermes SSH PID was replaced by a different PID, old process exited, count returned to one, access stayed ON, endpoint returned OPEN, and the already-open Hermes RDP session recovered automatically after a brief connection-lost interval.
- **RL-002 temporary Windows-side network loss — PASS**: the old Hermes SSH process exited under a scoped network block; after network restoration the agent automatically created one different SSH process with no Telegram command and access still enabled. RDP worked again. The test intentionally exceeded the Microsoft RDP client's reconnect window; that open client window then required manual reconnect.
- **RL-003 Linux server reboot — PASS**: pre-reboot both Hermes services were enabled+active with `:7000` and the tested RDP endpoint listening; after a real server reboot the server returned, Telegram/dashboard recovered, and the already-open Hermes RDP session restored automatically.

Current queue:

1. **Controller restart -> controller recovers while dedicated sshd/RDP transport stays healthy.**
2. Dedicated Hermes sshd restart -> clients recover.
3. Repeated reconnects -> no duplicate/orphan Hermes SSH processes.
4. Two+ devices simultaneously remain healthy.
5. Failure of one device does not affect another.

Windows reboot recovery is already PASS and is not repeated without a regression reason.

For RL-004, restart only `hermes-rdp.service`, not `hermes-rdp-sshd.service`. Keep an active Hermes RDP session open. Acceptance: controller PID changes and service returns active; dedicated sshd stays active; reverse-tunnel endpoint stays available; Telegram/dashboard returns; Windows-side ON/RESTART is not needed; and the active RDP transport remains usable. Any RDP interruption must be recorded explicitly.

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
