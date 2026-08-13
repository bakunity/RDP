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

### SEC-005 deterministic released-port reuse — FAIL / CONFIRMED INSTALLER STARTUP + RETRY BUG

A genuinely clean Windows PC passed the precheck with no Hermes config, key, task or process. Fresh pairing using the normal Telegram installer then failed after pairing with `SSH-туннель не запустился`; `agent.log` contained only the startup line.

Source-level contradiction confirms an installer/agent startup race: the installer starts the Scheduled Task, sleeps only 8 seconds, then requires an `ssh.exe` process or aborts. The accepted PR #20 control-first agent performs telemetry/API control work before transport reconciliation, and its pinned HTTP client may wait up to 20 seconds. Therefore a healthy fresh agent is allowed to still be inside its initial control cycle when the installer declares tunnel startup failure.

Post-failure Windows evidence: the installer catch successfully removed the Scheduled Task and stopped both the agent and SSH processes, but left `device.json`, the Ed25519 private key and public key on disk. The failed identity had been assigned released port `53391`. This residual state is itself a retry-path defect: the normal Add installer guard sees a valid local config plus keypair and will treat the machine as already installed even if `revoke-self` successfully removed the server registration.

Post-failure server evidence is PASS: `revoke-self` removed the failed registration, `53391` is unassigned, not listening and allocator-selected again as the next free port; MIPC remained registered with an open endpoint and fresh telemetry. The server is clean for a retry once the installer is fixed. This confirms the defect is in Windows installer startup/rollback behavior, not in hard revoke or port reuse.

Do not rerun Add on the test PC until cleanup/retry semantics are fixed or the bounded local residue cleanup is explicitly performed.

## Exact next action

Implement the SEC-005 installer fix on a dedicated branch: replace the fixed 8-second SSH assumption with bounded readiness polling compatible with control-first agent timing, and make failed fresh-install rollback remove local config/key residue only after `revoke-self` succeeds so Add can be retried safely. Add regression coverage, run Windows PowerShell 5.1 + Linux CI, then clean the failed test PC residue and retry SEC-005 with a new one-time pairing code.

Remaining Stage 3 gates after SEC-005: owner-limited Telegram authorization, admin SSH :22 independence from tunnel sshd :7000, and confirmation that no Defender exclusions/security weakening are required.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
