# Hermes RDP — Active Work

Updated: 2026-08-13

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Repository / release

- Repository: `bakunity/RDP`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- PR #19, PR #20 and PR #21 are merged and accepted.
- PR #21 merge commit: `12ba13080e25e935fb7cc17ece7852005c964c29`.

## Deployment truth

- Live controller/app is deployed from immutable PR #20 head `77240e2d758f0ed4598553d4d903331229653f06`.
- Final controller-only deploy passed: controller active, `/healthz` OK, configured repository ref exact.
- Dedicated `hermes-rdp-sshd.service` was not restarted by that deploy.
- MIPC accepted Windows agent is the PR #20 control-first agent; later PR #20 changes did not touch the Windows agent.
- PR #21 changes Windows installer behavior and tests; no production Linux service deploy was required for SEC-005 acceptance.

## Stage 2 lifecycle

- RL-001..RL-005: COMPLETE PASS.
- RL-006: PARTIAL PASS; five-cycle server-side reconnect stress passed, only one optional deferred Windows process-count check remains on the exact original device.
- RL-007: COMPLETE PASS.
- RL-008: COMPLETE PASS.

## Stage 3 — Device / Security lifecycle — ACTIVE

### SEC-001 device identity uniqueness — COMPLETE PASS

Live inventory showed unique Ed25519 SSH public keys, RDP ports, device IDs and API token hashes. No duplicates were present.

### SEC-002 cross-device SSH isolation — COMPLETE PASS

Effective sshd policy and actual `AuthorizedKeysCommand` mapped each active key only to its own device and own `permitlisten` port. An unregistered Ed25519 key was denied. Live negative-forward acceptance on MIPC also passed: the registered MIPC key authenticated, but an unauthorized reverse port was rejected while the normal assigned tunnel stayed up.

### SEC-003 hard revoke / DELETE lifecycle — COMPLETE PASS

The intentionally retired `ai` device was used as the destructive test object after a protected SQLite backup was created. Telegram DELETE hard-removed the registration. Post-delete live acceptance proved the old device record, token hash and SSH public key are absent from the current registry; the old SSH key is denied; the old endpoint remained closed; the old RDP port became unassigned/reusable; MIPC remained healthy throughout.

Do not restore the deleted `ai` registration from backup during normal continuation. The backup exists only as rollback/evidence for the bounded test.

### SEC-004 stale deleted-client reclaim — NOT LIVE-EXERCISED / FIXTURE UNAVAILABLE

The expected retired client archive was absent, and the bounded read-only search returned no matching deleted `ai` local identity. This is not a product FAIL and does not invalidate SEC-003. Do not reconstruct or expose old token/private-key material merely to manufacture the test.

### SEC-005 deterministic released-port reuse — RESOLVED / LIVE-ACCEPTED

Initial fresh install on a genuinely clean Windows PC exposed two real installer bugs:

- fixed 8-second post-task startup assumption raced the control-first agent before SSH transport reconciliation;
- after successful server `revoke-self`, local `device.json` and Ed25519 keypair residue remained and blocked a clean Add retry.

Server rollback after the failed attempt passed: failed registration removed, released port `53391` closed/unassigned and allocator-selected again, MIPC unaffected.

PR #21 `fix: harden Windows installer startup readiness` implemented bounded readiness polling, stable matching SSH-PID acceptance, richer startup diagnostics, explicit pairing-start state, safe snapshot restoration after known successful `revoke-self`, and credential preservation when pairing/revoke outcome is uncertain. Regression tests were added.

Exact live-tested code boundary before merge: `bc286d7abaf3cd8a712f92ec7f633dba8cd4547d`. Current PR head before merge was `d1f901a070aa8db006059378d263d7b72214fbb4`; CI #234 was COMPLETE PASS.

Live retry acceptance on Windows passed:

- installer reached `=== ГОТОВО ===`;
- a fresh device identity and fresh Ed25519 key were created;
- released port `53391` was reused;
- Scheduled Task stayed Running with exactly one matching Hermes SSH process;
- current identity/key differed from the archived failed attempt;
- final Linux post-check showed one active owner of `53391`, fresh telemetry, listener open, TCP-through-tunnel working, failed identity absent, deleted prior device identity/key not reused, and MIPC healthy;
- user successfully connected through Microsoft RDP to the reused endpoint.

PR #21 was merged using expected head `d1f901a070aa8db006059378d263d7b72214fbb4`; merge commit `12ba13080e25e935fb7cc17ece7852005c964c29`.

Do not repeat SEC-005 without a concrete installer/allocator regression reason.

### SEC-006 owner-limited Telegram authorization — COMPLETE PASS

Source inspection established one configured `telegram_chat_id`. `TelegramBot._authorized()` requires both the update chat ID and acting user ID to equal that configured owner ID; unauthorized messages return before any device/control mutation path.

Bounded live-config synthetic authorization check passed without Telegram API calls, registry writes or owner-ID output:

- owner in owner/private chat: allowed;
- wrong actor in owner chat: denied;
- owner in wrong chat: denied;
- wrong actor/wrong chat: denied;
- unauthorized callback actor: denied.

No source change is required. Do not repeat SEC-006 without an authorization-model regression reason.

### SEC-007 admin SSH independence from Hermes tunnel sshd — ACTIVE

Source boundary confirms Hermes uses a dedicated OpenSSH daemon with its own `/etc/hermes-rdp/sshd_config`, dedicated host key, PID file and systemd service. The tunnel daemon listens on configured `ssh_bind_port` (default `7000`) and is started as `sshd -D -e -f /etc/hermes-rdp/sshd_config`; it does not modify or replace the system/admin sshd configuration. The installer separately opens the configured Hermes tunnel port in UFW.

The remaining acceptance is a read-only live server check proving system/admin SSH `:22` and Hermes tunnel SSH `:7000` are owned by distinct listeners/process/service boundaries and both remain healthy simultaneously. Do not restart either sshd during this check.

## Exact next action

Run the read-only **SEC-007 SSH independence inventory** on Linux: inspect listeners/PIDs for ports `22` and configured Hermes `ssh_bind_port`, resolve each process command line and cgroup/systemd unit, verify Hermes uses `/etc/hermes-rdp/sshd_config`, verify admin listener is not the Hermes service, and confirm both ports accept TCP locally. If PASS, proceed to the final Stage 3 gate: confirmation that Hermes requires no Defender exclusions or other security weakening.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.