# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-13

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

PR #19 through PR #23 are merged and accepted. Lifecycle recovery/isolation and the full device/security stage are complete. Server and Windows transactional updater success/rollback paths are live-accepted. SEC-004 remains honestly fixture-unavailable; do not manufacture deleted credentials.

## Immediate work

### 1. Command / pairing / repair UX

This is the current product stage.

- keep `Добавить ПК` as fresh pairing only and make its existing-install refusal clear;
- add deterministic expired-pair retry UX;
- expose an explicit repair/update flow distinct from fresh pairing;
- preserve existing device registration, config/token, Ed25519 keypair, known-hosts and assigned port during repair;
- recover missing/broken local agent or Scheduled Task without silently creating a second device;
- distinguish healthy update from repair-needed state;
- provide bounded recovery diagnostics without exposing secret material;
- keep Windows PowerShell 5.1 and Win10 x64/x86-PowerShell compatibility;
- finish Russian dashboard terminology and edge-state text where needed.

Implement with regression coverage and CI first. Then use a bounded non-critical Windows fixture for any repair mutation acceptance.

### 2. Documentation / website / release

Before the `v1.2.0` tag:

- reconcile release notes with accepted evidence;
- archive release evidence and compact active context;
- ensure docs match current runtime/security/update/repair model;
- document updater rollback and repair/recovery paths;
- publish immutable tag/release;
- then continue website v2 after runtime stabilization.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` check after five already-clean server-side reconnect cycles. If that exact machine is later identified, collect only that one count. Do not repeat the five-cycle stress test.

## Context-system follow-up

Optional after release work: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
