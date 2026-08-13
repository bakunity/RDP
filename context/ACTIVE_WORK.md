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

### SEC-004 stale deleted-client reclaim — TEST FIXTURE UNAVAILABLE

The expected retired Windows archive path `C:\ProgramData\HermesRDP.pre-x86-20260810-083418` was checked on the candidate PC and does not exist there; `device.json` is therefore unavailable at that path. This is not a product FAIL and does not weaken SEC-003 server-side revoke evidence. Do not manufacture old API tokens or private keys from server data.

If another local `HermesRDP*` directory containing the deleted `ai` identity exists, a bounded old-client negative test may still be performed. Otherwise keep SEC-004 as not live-exercised due missing client fixture and move to deterministic port-reuse acceptance with a fresh identity.

## Exact next action

Perform one read-only search on the retired Windows PC for any `C:\ProgramData\HermesRDP*` directories and identify whether any `device.json` still matches deleted `ai` (`:53391`) without printing secrets. If none exists, stop searching and proceed to safe deterministic port reuse with a fresh identity.

Remaining Stage 3 gates after that: safe deterministic port reuse with a new identity, owner-limited Telegram authorization, admin SSH :22 independence from tunnel sshd :7000, and confirmation that no Defender exclusions/security weakening are required.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not raw terminal transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
