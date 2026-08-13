# Hermes RDP — Current State Snapshot

Updated: 2026-08-13

For immediate operational truth read `ACTIVE_WORK.md`; for scenario-level proof/revalidation read `EVIDENCE_LEDGER.md`.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0` — OpenSSH transition release.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 merged and accepted.
- PR #20 merged; merge commit `dcda9d3890be390a90e9a967905f2cab3c6c7194`.
- PR #21 merged; merge commit `12ba13080e25e935fb7cc17ece7852005c964c29`.

## Architecture — current

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd :7000
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent public endpoint per device
```

Durable boundaries remain: all Windows machines are equal clients; Linux is infrastructure-special; admin SSH `:22` is independent from Hermes tunnel SSH; FRP is not active runtime; private per-device SSH keys remain on Windows; Telegram is control plane rather than RDP transport.

## Deployment truth

- Live controller/app remains deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Dedicated Hermes sshd is separate from system/admin sshd.
- MIPC accepted Windows agent remains the PR #20 control-first agent.
- PR #21 changed Windows fresh-install readiness/rollback behavior and required no Linux service deploy.

## Stable accepted baseline

Do not re-run wholesale without a concrete regression reason:

- OpenSSH reverse RDP end-to-end / external-network RDP;
- Windows reboot recovery;
- MIPC performance/classification/Observe60;
- Windows Server 2019 acceptance;
- Win10 x64 + PowerShell x86/Sysnative acceptance;
- RL-001..RL-005, RL-007, RL-008;
- CP-001, CL-001, CU-001;
- Telegram dashboard auto-refresh/mobile layout;
- SEC-001 unique per-device identity;
- SEC-002 cross-device SSH/forward isolation;
- SEC-003 hard DELETE/revoke lifecycle;
- SEC-005 deterministic safe released-port reuse + installer retry fix;
- SEC-006 owner-limited Telegram authorization;
- SEC-007 admin SSH / Hermes sshd independence;
- SEC-008 Hermes operation with normal Defender real-time/behavior protection and no exclusions.

## Stage 3 device/security evidence

**SEC-001 — COMPLETE PASS.** Unique IDs, token hashes, Ed25519 keys and RDP ports.

**SEC-002 — COMPLETE PASS.** Valid keys are restricted to their own endpoint; unregistered/unauthorized forwarding is denied.

**SEC-003 — COMPLETE PASS.** Hard DELETE removes API/SSH authorization and releases the endpoint/port without harming the healthy control device.

**SEC-004 — NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE.** The deleted old-client fixture no longer exists. Do not reconstruct credentials just to manufacture the test.

**SEC-005 — RESOLVED / LIVE-ACCEPTED.** PR #21 fixed fresh-install readiness and failed-install rollback/retry behavior; released port reuse passed with a genuinely new identity/key and real RDP.

**SEC-006 — COMPLETE PASS.** Only configured owner + configured private chat is authorized.

**SEC-007 — COMPLETE PASS.** Admin SSH `:22` and Hermes sshd `:7000` are distinct healthy service/process/config boundaries.

**SEC-008 — COMPLETE PASS.** Initial Defender failure was a pre-existing local policy on the unmanaged Hyper-V test VM. After restoring normal Defender state, final acceptance showed real-time and behavior protection enabled, no Hermes/broad exclusions, Hermes task Running, exactly one Hermes SSH process, same endpoint, and the user remained connected through Hermes RDP throughout the protection-enable/final-check sequence.

Stage 3 is therefore **COMPLETE**, with SEC-004 intentionally retained as fixture-unavailable rather than falsely marked live-tested.

## Stage 2 deferred item

**RL-006 — PARTIAL PASS.** Five repeated dedicated-sshd reconnect cycles were clean server-side. The final one-process check on the exact original Windows device remains optional/deferred; do not repeat the stress sequence.

## Current release gate

Proceed to **safe migration / updater / rollback hardening**. First inspect current server updater and Windows update/repair behavior read-only: immutable-source provenance, deployed SHA recording, backup scope, post-update health gates, identity/config preservation and rollback semantics. Only after the boundaries are documented should live update/rollback acceptance be designed.
