# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-12

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Current release target

**Hermes RDP v1.2.0 — Stabilization**

PR #19 is merged and its acceptance remains valid. Long-lived soak testing discovered new release blockers outside that original scope.

## Immediate stabilization blockers — ACTIVE

Lifecycle matrix work is paused before RL-007/RL-008 completion until the following are fixed.

### 1. CP-001 — HTTPS API TLS accept stall

Confirmed live after long-lived operation: controller process remained `active` and `:7443` remained listening, but local `/healthz` timed out, listener backlog saturated, an external connection remained established, and the API thread blocked in socket receive. All Windows heartbeat/telemetry stopped while independent OpenSSH reverse tunnels remained alive. Controller-only restart restored API and telemetry without touching dedicated sshd.

Required implementation:

- accept raw TCP first;
- perform TLS handshake inside the per-connection worker rather than on the shared listening socket;
- enforce a short handshake timeout and bounded request I/O timeout;
- malformed/slow clients must only consume their own worker and must not block new accepts;
- regression test must demonstrate a deliberately stalled TLS client cannot stop `/healthz` or a second normal request.

### 2. CL-001 — transport failure blocks heartbeat/control

Confirmed live on OSIO. Server desired state became OFF while Windows local state was still ON. Server correctly rejected OSIO's SSH key because desired `enabled=0`; the rejected fingerprint exactly matched OSIO's registered key. Windows agent tried `Start-SshTunnel` before `/telemetry`, the SSH failure aborted the cycle, and the agent therefore could not receive its pending OFF command.

Required implementation:

- heartbeat/control polling must run even if SSH start/recovery fails;
- transport reconciliation must be isolated from API polling errors;
- desired OFF must converge from local ON without requiring successful SSH authentication;
- failed transport start should be reportable as telemetry/error state rather than suppressing heartbeat;
- regression test must cover server desired OFF + local ON + SSH authorization failure and prove command delivery still occurs.

### 3. CU-001 — deterministic command status/timeout

Live OSIO command remained pending for many hours and Telegram kept showing execution. Required design must distinguish desired state from command-delivery/result state so a UI timeout does not destroy eventual desired-state convergence when an offline device returns.

Minimum v1.2.0 outcome:

- no endless "executing" state;
- explicit queued/offline/timeout/failure semantics;
- overlapping command behavior remains deterministic;
- returning client still converges to current desired access state.

## Stage 2 evidence retained

- RL-001..RL-005: COMPLETE PASS.
- RL-006: server-side PASS after five repeated reconnects; final Windows process-count check deferred. Do not repeat the stress sequence.
- RL-007: four simultaneous endpoint listeners and TCP-through-tunnel checks PASS server-side; user-facing completion paused by the blockers above.
- RL-008: not yet run.

After the stabilization fix is CI-green and live-accepted, resume with the smallest remaining RL-006 Windows count check if available, then finish RL-007 and RL-008.

## Next implementation sequence

1. Create a dedicated fix branch from current `main`.
2. Fix server TLS accept/handshake lifecycle with regression tests.
3. Fix Windows heartbeat/control ordering with regression tests and PowerShell 5.1 parsing.
4. Add command timeout/status semantics without conflating desired state with delivery state.
5. Run full Linux + Windows CI.
6. Deploy server fix with rollback anchor; verify API stays responsive under a stalled TLS connection.
7. Update one Windows test client; reproduce the former OSIO deadlock in bounded form and prove heartbeat/command convergence.
8. Roll out to remaining test clients, then resume RL-007/RL-008.

## Later stages

### Device/security lifecycle

Verify unique Ed25519 identity, cross-device isolation, key revocation, DELETE behavior, safe port reuse, owner-limited Telegram authorization, admin-SSH independence, and no Defender exclusions.

### Safe migration / updater / rollback

Harden legacy Windows archival, server updater provenance/rollback and Windows updater health/rollback. Server updater still needs immutable-source resolution and deployed-SHA recording.

### Command / pairing / repair UX

After CU-001 is resolved: expired-pair retry UX, explicit repair/update flow, and final Russian dashboard terminology.

### Documentation / website / release

Rebuild docs and Website v2 only after runtime behavior stabilizes. Before v1.2.0 tag: reconcile release notes with evidence, archive release evidence, compact active context, ensure docs match runtime, publish immutable tag and document rollback/recovery.

## Context-system follow-up

Optional after lifecycle work: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
