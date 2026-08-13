# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 is merged and accepted.
- PR #20 (`fix: prevent soak-time control plane deadlocks`) is merged into `main` as `dcda9d3890be390a90e9a967905f2cab3c6c7194`.

## Deployment truth

- Live controller/app is deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy passed: controller active, `/healthz` OK, configured repository ref exact, rollback backup `/var/backups/hermes-rdp/controller-20260812T095505Z`.
- Dedicated `hermes-rdp-sshd.service` was not restarted by the final deploy; PID remained unchanged, preserving active OpenSSH transport.
- MIPC agent live acceptance used immutable head `2a170b0f4961299227120afa2eb7c0fffb0f0d13`; subsequent PR #20 changes touched only server bot/registry/tests, not the Windows agent.

## Stabilization blockers — CLOSED

CP-001, CL-001 and CU-001 are COMPLETE PASS and must not be repeated without a concrete regression reason. Telegram dashboard auto-refresh and mobile control-button layout are also live-accepted.

## Stage 2 lifecycle

- RL-001..RL-005: COMPLETE PASS.
- RL-006: PARTIAL PASS; server-side five-cycle reconnect stress passed, only one deferred Windows process-count closure remains. Do not repeat the stress.
- RL-007: COMPLETE PASS; two simultaneous Microsoft RDP sessions to different Hermes devices worked concurrently.
- RL-008: COMPLETE PASS; holding only MIPC OFF dropped only MIPC while other device/session remained stable, shared service PIDs stayed unchanged, and MIPC restored automatically.

## Stage 3 — Device / Security lifecycle — ACTIVE

### SEC-001 device identity uniqueness — COMPLETE PASS

Live inventory of five active devices showed every device has an Ed25519 SSH key, unique SSH public key, unique RDP port, unique device ID and unique API token hash. No duplicates were present.

### SEC-002 cross-device SSH isolation — POLICY PASS

Live effective `sshd -T` policy verified public-key-only auth, remote forwarding only, `PermitOpen none`, no TTY/agent/X11/session channels, and the Hermes `AuthorizedKeysCommand`. For every active device, registry and actual AuthorizedKeysCommand mapped its key back to itself and emitted only its own `permitlisten="0.0.0.0:<rdp_port>"`. A syntactically valid unregistered Ed25519 public key was denied. No device exposed any other registered RDP port through its authorization line.

Remaining SEC-002 gate: one bounded live OpenSSH negative-forward test with a real registered client key requesting a free but unauthorized reverse port. Existing primary tunnel must remain running; failure must be due the server permitlisten restriction, not port collision.

## Exact next action

Select one currently unused RDP-range port on the server and verify it is both unassigned in the registry and not listening. Then use MIPC's existing private key in a second one-shot SSH connection to request that unauthorized reverse port. Expected result: authentication may succeed, but `ExitOnForwardFailure=yes` must return remote port forwarding failure while MIPC's normal assigned tunnel remains unaffected.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
