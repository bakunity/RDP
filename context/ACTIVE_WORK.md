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

### SEC-002 cross-device SSH isolation — COMPLETE PASS

Policy acceptance passed: live effective `sshd -T` verified public-key-only authentication, remote forwarding only, `PermitOpen none`, no TTY/agent/X11/session channels, and Hermes `AuthorizedKeysCommand`. Every active key mapped only to its own device and emitted only its own `permitlisten="0.0.0.0:<rdp_port>"`; an unregistered Ed25519 key was denied.

Live negative-forward acceptance also passed on MIPC: its real registered key authenticated successfully, then a second one-shot SSH connection requesting free but unauthorized reverse port `53420` was rejected by the server. The process exited, the log contained both successful public-key authentication and remote-forward denial, and the normal assigned MIPC tunnel remained separate. The PowerShell result did not retain a numeric exit code because `if/else` was pasted interactively as separate statements, but that does not invalidate the observed authenticated-then-denied server behavior.

## Exact next action

Proceed to **SEC-003 hard revoke / DELETE lifecycle**. Use a disposable or intentionally retired device if available; do not delete MIPC or another required production device. Acceptance must prove that after hard revoke the old API token no longer authenticates, the old SSH key no longer authorizes, the old endpoint cannot return, and the released RDP port becomes safely reusable. Preserve one healthy control device throughout.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
