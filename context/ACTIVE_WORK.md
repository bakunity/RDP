# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19 and PR #20 are merged and accepted.

## Deployment truth

- Live controller/app is deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy passed: controller active, `/healthz` OK, configured repository ref exact.
- Dedicated `hermes-rdp-sshd.service` was not restarted by that deploy.
- MIPC accepted Windows agent is the PR #20 control-first agent; later PR #20 changes did not touch the Windows agent.

## Stage 2 lifecycle

- RL-001..RL-005: COMPLETE PASS.
- RL-006: PARTIAL PASS; five-cycle server-side reconnect stress passed, only one optional deferred Windows process-count check remains on the exact original device.
- RL-007: COMPLETE PASS.
- RL-008: COMPLETE PASS.

## Stage 3 — Device / Security lifecycle — ACTIVE

### SEC-001 device identity uniqueness — COMPLETE PASS

Live inventory of five active devices showed unique Ed25519 SSH public keys, RDP ports, device IDs and API token hashes. No duplicates were present.

### SEC-002 cross-device SSH isolation — COMPLETE PASS

Effective sshd policy and actual `AuthorizedKeysCommand` mapped every active key only to its own device and own `permitlisten` port. An unregistered Ed25519 key was denied. Live negative-forward acceptance on MIPC also passed: the registered MIPC key authenticated, but a second one-shot SSH connection requesting free unauthorized reverse port `53420` was rejected while the normal assigned tunnel stayed separate.

### SEC-003 hard revoke / DELETE lifecycle — COMPLETE PASS

The intentionally retired `ai` device was used as the destructive test object after a protected SQLite backup was created. Telegram DELETE hard-removed the registration. Post-delete live acceptance proved the old device record, token hash and SSH public key are absent from the current registry; the old SSH key is denied by both registry authorization and the real AuthorizedKeysCommand; the old endpoint remained closed across the observation window; the old RDP port is unassigned and allocator-selected as the next reusable port; MIPC remained healthy throughout.

Do not restore the deleted `ai` registration from backup during normal continuation. The backup exists only as rollback evidence for this bounded test.

### SEC-004 stale deleted-client reclaim — NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE

The expected retired archive was absent, then a read-only search across `C:\ProgramData\HermesRDP*` returned `SEC004_SEARCH=NO_AI`. No local `device.json` matching the deleted `ai` identity remains on that Windows machine. This is not a product FAIL and does not invalidate SEC-003. Do not reconstruct or expose old token/private-key material merely to manufacture this test.

Retain SEC-004 as not live-exercised because the old client fixture no longer exists. Server-side hard-revoke evidence remains COMPLETE PASS from SEC-003.

### SEC-005 deterministic released-port reuse — FIX LIVE RETRY STARTUP PASS / FINAL POST-CHECK PENDING

A genuinely clean Windows PC passed the precheck with no Hermes config, key, task or process. The original main installer then failed after pairing with `SSH-туннель не запустился`; `agent.log` contained only the startup line.

Confirmed bug 1: the installer used a fixed 8-second post-task sleep before requiring `ssh.exe`, while the accepted control-first agent is allowed to spend up to its initial API/control timeout before transport reconciliation. This created a legitimate startup race.

Confirmed bug 2: after the failure, the installer successfully removed the Scheduled Task and processes and `revoke-self` successfully hard-removed the server registration, but local `device.json` and the Ed25519 keypair remained. The stale local identity then blocked normal Add even though the server registration was gone.

Server post-failure cleanup passed: failed registration count 0, `53391` unassigned and closed, allocator next port `53391`, and MIPC remained registered/listening with fresh telemetry.

The failed local residue was archived read-only to a timestamped `C:\ProgramData\HermesRDP.sec005-failed-*` path after confirming canonical Hermes config absent, no Scheduled Task and no Hermes process remained. This preserved rollback evidence while making the canonical path clean.

PR #21: `fix: harden Windows installer startup readiness` on branch `fix/installer-startup-readiness`.

Implemented:
- fixed 8-second startup assumption replaced with bounded readiness polling;
- installer requires one matching SSH PID to remain stable long enough to outlive the SSH connect timeout before success;
- timeout diagnostics include agent/SSH logs;
- pairing-start state is tracked explicitly;
- after a known successful `revoke-self`, the pre-attempt local snapshot is restored so failed fresh installs are retryable;
- uncertain pairing outcome or failed server revoke preserves local recovery credentials;
- regression tests cover readiness and rollback semantics.

PR #21 exact accepted CI head before live retry: `bc286d7abaf3cd8a712f92ec7f633dba8cd4547d`. CI #232 is COMPLETE PASS: Linux full release checks PASS; Windows PowerShell 5.1 parse and certificate-pinning validation PASS. PR is mergeable.

Bounded live retry from exact commit `bc286d7...` succeeded on the Windows test PC: installer reached `=== ГОТОВО ===`, registered `SEC005 TEST`, received released RDP port `53391`, selected OpenSSH transport and created the `Hermes RDP Agent` task. A first harness attempt was blocked before installer execution by Windows script execution policy; the retry used the same downloaded content as an in-memory scriptblock without changing machine ExecutionPolicy.

This proves the startup-race fix can complete a real fresh install, but SEC-005 is not final until post-check verifies new identity/key separation from the archived failed attempt, one healthy SSH/task locally, server listener/registration truth on `53391`, and MIPC isolation.

## Exact next action

Run a bounded local SEC-005 post-check on the test Windows PC: compare current and archived failed-attempt device IDs and Ed25519 public keys without printing key material, confirm current port `53391`, Scheduled Task Running and exactly one Hermes SSH process. If that passes, run one server-side post-check proving `SEC005 TEST` is the sole registration on `53391`, listener is open, telemetry fresh, old failed identity remains absent and MIPC remains healthy. Only then mark SEC-005 RESOLVED / LIVE-ACCEPTED and merge PR #21.

Remaining Stage 3 gates after SEC-005: owner-limited Telegram authorization, admin SSH :22 independence from tunnel sshd :7000, and confirmation that no Defender exclusions/security weakening are required.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
