# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-12

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

PR #19 is merged and accepted. PR #20 is merged and live-accepted; the soak blockers CP-001, CL-001 and CU-001 are closed. RL-007 simultaneous multi-device user smoke is also COMPLETE PASS.

## Immediate work — Stage 2 lifecycle completion

### 1. RL-008 — one-device failure isolation

Deliberately disturb only one selected test device/transport and verify another healthy device remains unaffected:

- keep a real Hermes RDP session open on healthy device B;
- apply the smallest reversible transport/client fault only to device A;
- verify device B heartbeat stays fresh;
- verify device B SSH tunnel/listener stays present;
- verify device B active RDP session remains usable;
- verify controller and dedicated sshd remain healthy.

Do not restart shared infrastructure. Do not repeat earlier CP/CL/CU or multi-cycle sshd stress.

### 2. RL-006 — optional final lightweight Windows count

Server-side repeated reconnect stress is already PASS after five clean dedicated-sshd cycles. Final Windows process count on the original tested machine was not collected. If that exact machine is available, perform only one check that normal ON state has exactly one Hermes `ssh.exe`. Do not repeat the five-cycle test.

## Completed Stage 2 evidence retained

- RL-001..RL-005: COMPLETE PASS.
- RL-007: four simultaneous server-side endpoints/TCP checks PASS plus two simultaneous user-facing Microsoft RDP sessions to different Hermes devices PASS.
- CP-001: per-connection TLS handshake + bounded timeout; live slow-client acceptance COMPLETE PASS.
- CL-001: heartbeat/control independent of SSH transport; direct desired OFF/local ON reconciliation COMPLETE PASS.
- CU-001: 60-second transient command timeout with durable desired state and late-result rejection; COMPLETE PASS.
- Telegram UI: automatic post-command dashboard refresh and full-width OFF/RESTART mobile layout; COMPLETE PASS.
- CI #210 on final PR #20 head: Windows PowerShell 5.1 PASS, Linux full release checks PASS.

## After Stage 2

### Device/security lifecycle

Verify unique Ed25519 identity, cross-device isolation, key revocation, DELETE behavior, safe port reuse, owner-limited Telegram authorization, admin-SSH independence, and no Defender exclusions.

### Safe migration / updater / rollback

Harden legacy Windows archival, server updater provenance/rollback and Windows updater health/rollback. Server updater still needs stronger immutable-source/deployed-SHA recording and explicit health-based rollback behavior.

### Command / pairing / repair UX

Add expired-pair retry UX, explicit repair/update flow, and finish Russian dashboard terminology where needed.

### Documentation / website / release

Before v1.2.0 tag: reconcile release notes with evidence, archive release evidence, compact active context, ensure docs match runtime, publish immutable tag, and document rollback/recovery. Website v2 follows runtime stabilization rather than preceding it.

## Context-system follow-up

Optional after lifecycle work: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
