# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-13

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

PR #19, PR #20 and PR #21 are merged and accepted. Lifecycle recovery/isolation and the full device/security stage are complete. SEC-004 remains honestly marked fixture-unavailable because the deleted old-client credentials no longer exist; do not manufacture them.

## Immediate work

### 1. Safe migration / updater / rollback hardening

This is the current full product stage.

First perform read-only source/runtime inventory before any live mutation:

- identify the current server update entry point and source-ref/provenance behavior;
- determine whether exact deployed commit/SHA is recorded and surfaced;
- verify backup scope and permissions;
- map pre-update and post-update health gates;
- determine whether failure after partial deployment causes automatic rollback;
- verify dedicated sshd/controller restart boundaries;
- inspect Windows update/repair path and whether it preserves device ID, API token, Ed25519 private key, RDP port and Scheduled Task state;
- verify rollback cannot silently leave mixed old/new files or broken permissions.

Then design bounded live acceptance with a known-good rollback anchor. Do not start with destructive update tests.

### 2. Command / pairing / repair UX

After updater/rollback hardening:

- add expired-pair retry UX;
- implement explicit repair/update flow distinct from `Добавить ПК`;
- finish Russian dashboard terminology/edge-state text where needed;
- make recovery actions clear without exposing secret material.

### 3. Documentation / website / release

Before the `v1.2.0` tag:

- reconcile release notes with accepted evidence;
- archive release evidence and compact active context;
- ensure docs match current runtime and security model;
- publish immutable tag/release;
- document rollback/recovery paths;
- then continue website v2 after runtime stabilization.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` check after five already-clean server-side reconnect cycles. If that exact machine is later identified, collect only that one count. Do not repeat the five-cycle stress test.

## Context-system follow-up

Optional after release work: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
