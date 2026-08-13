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

### SEC-006 owner-limited Telegram authorization — SOURCE BOUNDARY CONFIRMED / LIVE NEGATIVE PENDING

Read-only source inspection confirms the controller has one configured `telegram_chat_id`. `TelegramBot._authorized()` extracts both the update chat ID and the acting user ID and returns true only when **both** equal that configured owner ID. Therefore an owner acting in a different/group chat is denied, and a different actor in the owner's chat is also denied. Unauthorized ordinary messages are ignored; unauthorized callbacks receive `Нет доступа` and return before callback/device mutation logic.

No source change is required at this point. The remaining acceptance is one bounded live-config authorization check that calls only `_authorized()` with synthetic updates and never invokes Telegram API, registry writes, device commands or secrets output.

## Exact next action

Run the read-only **SEC-006 live-config negative authorization check** on the Linux server. It should prove owner/private-chat = allowed, wrong actor in owner chat = denied, owner in wrong chat = denied, and wrong actor/wrong chat = denied without printing the real owner ID. If PASS, mark SEC-006 COMPLETE and proceed to admin SSH `:22` independence from Hermes sshd `:7000`.

Remaining Stage 3 gate after that: confirmation that Hermes requires no Defender exclusions or other security weakening.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
