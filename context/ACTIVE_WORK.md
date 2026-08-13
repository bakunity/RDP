# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs in the evidence/history files.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, PR #20 and PR #21 are merged and accepted.
- PR #21 merge commit: `12ba13080e25e935fb7cc17ece7852005c964c29`.

## Deployment truth

- Live controller/app remains deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Dedicated `hermes-rdp-sshd.service` remains separate from admin SSH.
- MIPC accepted Windows agent remains the PR #20 control-first agent.
- PR #21 changed Windows fresh-install readiness/rollback behavior and required no production Linux service deploy.

## Stage 2 lifecycle

- RL-001..RL-005: COMPLETE PASS.
- RL-006: PARTIAL PASS; five-cycle server-side reconnect stress passed, with only the optional original-machine one-process check uncollected.
- RL-007: COMPLETE PASS.
- RL-008: COMPLETE PASS.

## Stage 3 — Device / Security lifecycle — COMPLETE

### SEC-001 device identity uniqueness — COMPLETE PASS

Active inventory proved unique device IDs, API token hashes, Ed25519 keys and RDP ports.

### SEC-002 cross-device SSH isolation — COMPLETE PASS

Each registered key is constrained to its own `permitlisten` endpoint. An unregistered key was denied and a valid device key could not request an unauthorized reverse port.

### SEC-003 hard revoke / DELETE lifecycle — COMPLETE PASS

Telegram DELETE hard-removed the retired device registration; its API/SSH authorization disappeared, endpoint stayed closed, port became reusable, and the healthy control device remained unaffected.

### SEC-004 stale deleted-client reclaim — NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE

The deleted client fixture no longer existed locally. Do not reconstruct secrets merely to manufacture this test. This is not a product FAIL and does not invalidate SEC-003.

### SEC-005 deterministic released-port reuse — RESOLVED / LIVE-ACCEPTED

PR #21 fixed the real fresh-install startup race and stale-local-residue retry problem. A genuinely fresh identity/key safely reused released port `53391`; local and server post-checks passed, MIPC stayed healthy, and real Microsoft RDP succeeded.

### SEC-006 owner-limited Telegram authorization — COMPLETE PASS

Live-config synthetic checks proved only the configured owner acting in the configured private chat is authorized; wrong actor/chat combinations and unauthorized callbacks are denied before mutation logic.

### SEC-007 admin SSH independence — COMPLETE PASS

Live inventory proved admin SSH `:22` and Hermes tunnel sshd `:7000` are distinct process/config/systemd boundaries and are healthy simultaneously.

### SEC-008 no Windows security weakening — COMPLETE PASS

Repository inspection found no Hermes Defender-disable or exclusion logic. Initial failure was traced to a pre-existing local `DisableRealtimeMonitoring=1` policy on the unmanaged Hyper-V test VM, not Hermes.

The local disabling policy was removed and normal Defender protection enabled. Final acceptance then proved simultaneously:

- `AMServiceEnabled=True`;
- `AntivirusEnabled=True`;
- `RealTimeProtectionEnabled=True`;
- `BehaviorMonitorEnabled=True`;
- `AMRunningMode=Normal`;
- policy `DisableRealtimeMonitoring` absent;
- no Hermes path/process exclusion;
- no broad `.ps1`/`.exe` exclusion;
- Hermes Scheduled Task Running;
- exactly one Hermes `ssh.exe`;
- device remained on `53391`.

The user was already connected to this VM through Hermes RDP for the whole Defender-enable/final-check sequence, so the active Hermes RDP session also remained usable while normal Defender real-time/behavior protection was enabled.

Do not restore the old local Defender-disable policy during normal continuation.

## Exact next action

Stage 3 is complete. Proceed to the next v1.2.0 stabilization stage: **safe migration / updater / rollback**.

Start with a read-only source/runtime inventory of the current server updater and Windows update/repair paths. Identify provenance recording, backup boundaries, health checks and automatic rollback behavior before changing code or running destructive update tests.

After updater/rollback hardening, remaining product work is command/pairing/repair UX, then release documentation/tagging.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
