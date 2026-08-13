# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-13

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

PR #19, PR #20, PR #21 and PR #22 are merged and accepted. Lifecycle recovery/isolation and the full device/security stage are complete. SEC-004 remains honestly marked fixture-unavailable because the deleted old-client credentials no longer exist; do not manufacture them.

## Immediate work

### 1. Windows updater / repair hardening

Server updater hardening is complete: PR #22 passed CI, live success-path acceptance and deliberate post-mutation automatic rollback acceptance.

Current Windows updater gaps to close:

- stage/download and parse the candidate before stopping a healthy running agent whenever possible;
- preserve device ID, API token/config, Ed25519 private/public key, known-hosts and assigned RDP port;
- preserve the existing Scheduled Task definition/state;
- take a bounded rollback snapshot of the current agent and relevant non-secret metadata;
- activate the candidate and require bounded readiness rather than merely `Start-ScheduledTask`;
- require exactly one matching Hermes `ssh.exe` in normal ON state;
- automatically restore the previous agent/task state if activation fails;
- surface useful diagnostics without exposing tokens/private keys;
- remain compatible with Windows PowerShell 5.1 and Win10 x64 under x86 PowerShell/Sysnative;
- keep explicit update/repair behavior distinct from fresh `Добавить ПК` pairing.

Add regression coverage and CI before any live destructive test. Then run a success-path update and a forced-failure rollback test on a non-critical Windows fixture.

### 2. Command / pairing / repair UX

After updater/repair transaction semantics are accepted:

- add expired-pair retry UX;
- expose explicit repair/update flow distinct from `Добавить ПК`;
- finish Russian dashboard terminology/edge-state text where needed;
- make recovery actions clear without exposing secret material.

### 3. Documentation / website / release

Before the `v1.2.0` tag:

- reconcile release notes with accepted evidence;
- archive release evidence and compact active context;
- ensure docs match current runtime and security model;
- document updater rollback/recovery paths;
- publish immutable tag/release;
- then continue website v2 after runtime stabilization.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` check after five already-clean server-side reconnect cycles. If that exact machine is later identified, collect only that one count. Do not repeat the five-cycle stress test.

## Context-system follow-up

Optional after release work: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
