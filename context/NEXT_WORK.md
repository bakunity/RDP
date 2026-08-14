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
- CERT-006 production Let’s Encrypt public-IP issuance: PASS.
- CERT-007 scheduler inventory: PASS; missing scheduler gap confirmed.
- CERT-008 Hermes-owned systemd renewal service/timer: live PASS, including unit verification, active/enabled timer, bounded service run and TCP 80 cleanup.

Active productization:

- draft PR **#29** on `feat/trusted-rdp-cert-lifecycle`, head `e914a0f45a6cc734d25b02340353fc06ace6c7c8`;
- lifecycle setup module, renewal wrapper and repository-owned systemd units implemented;
- `install-server.sh --trusted-rdp-cert` explicit opt-in implemented while default install remains unchanged;
- uninstall removes Hermes-owned units/wrapper but preserves ACME lineage;
- CI #313 PASS on Linux + Windows PowerShell 5.1;
- CI #316 PASS after installer/uninstall wiring on Linux + Windows PowerShell 5.1.

Next:

- **CERT-009:** live-accept PR #29 certificate setup module on the current certificate host using the immutable PR head; it must reuse the existing production lineage, not request another certificate, install/adopt repository-owned renewal units, preserve certificate serial and leave TCP 80 free;
- after live acceptance, reconcile/checkpoint PR #29 and decide merge readiness;
- design authenticated delivery/rotation of the short-lived certificate to Windows devices;
- do not expose a shared private key through a weak endpoint;
- bind/test first on `SEC005 TEST` with the previous RDP listener certificate/state preserved for rollback;
- validate the actual Microsoft Remote Desktop trust/name warning before wider rollout;
- after Windows acceptance, make the certificate lifecycle a polished normal Hermes installation flow rather than an expert/manual feature.

Architecture note: one separate Let’s Encrypt public-IP certificate per Windows device does not scale as the default design because all devices share the same IP identifier and the CA limits new certificates for an exact identifier set. Current scalable direction is one short-lived lineage per Hermes server plus a strongly authenticated rotation mechanism.

### 2. Release automation hardening

- review/merge prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`;
- release workflow must tag the exact validated workflow `HEAD`;
- retain the regression assertion;
- do not alter published `v1.2.0` or `v1.2.1` tags.

### 3. Post-release docs / website

After certificate behavior is accepted:

- document public-IP trusted RDP certificate requirements, renewal and Windows rotation;
- reconcile website messaging with the stable release and product README;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.

## Context-system follow-up

Optional later: compact/reconcile `EVIDENCE_LEDGER.md` at a release boundary and add lightweight context-hygiene/lint checks.
