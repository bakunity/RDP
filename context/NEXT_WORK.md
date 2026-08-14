# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Use `v1.2.1` for new installs and updates; do not rewrite historical `v1.2.0`.

## Immediate work

### 1. Trusted RDP certificate on public IP

Already complete:

- CERT-001 server inventory: PASS.
- CERT-002 Certbot 5.7.0 installation: PASS.
- CERT-003 public HTTP-01 reachability through UFW/TCP 80: PASS.
- CERT-004 Let’s Encrypt staging public-IP issuance: PASS.
- CERT-005 staging key/fullchain/renewal mechanics and dry-run: PASS.
- CERT-006 real production Let’s Encrypt public-IP issuance: PASS.
- CERT-007 automatic-renewal scheduler inventory: PASS; **gap confirmed** — this pip/venv installation has no systemd timer/service and no cron entry running `certbot renew`.

Next:

- **CERT-008:** install a Hermes-owned systemd service/timer for periodic normal `certbot renew`, with persistent scheduling, randomized delay, locking/logging/failure visibility; validate unit files, next run and a bounded manual service invocation;
- add a deploy hook only after scheduler acceptance, so Windows rotation happens only after a successful renewal;
- design the secure Windows certificate/private-key model; do not casually copy one shared private key to every device;
- integrate ACME installation, issuance, renewal and rotation into Hermes RDP server/client flows so normal operation does not require manual shell commands;
- bind/test first on non-critical `SEC005 TEST`, preserving the previous RDP listener certificate/state as rollback;
- validate Microsoft Remote Desktop no longer reports the intended trust/name warning;
- only then expand to other Windows devices.

Do not mutate Windows/RDP until server-side issuance and automatic renewal are proven.

### 2. Release automation hardening

- review/merge prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`;
- release workflow must tag the exact validated workflow `HEAD`;
- retain the regression assertion;
- do not alter published `v1.2.0` or `v1.2.1` tags.

### 3. Post-release docs / website

After certificate behavior is accepted:

- document public-IP trusted RDP certificate requirements and renewal;
- reconcile website messaging with `v1.2.1` and the full product README;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.

## Context-system follow-up

Optional later: compact/reconcile `EVIDENCE_LEDGER.md` at a release boundary and add lightweight context-hygiene/lint checks.
