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
- CERT-008 Hermes-owned systemd renewal service/timer: live PASS.
- CERT-009 productized server lifecycle on immutable PR #29 head: live PASS; existing certificate reused, serial preserved, timer active/enabled, smoke PASS_NOT_DUE, TCP 80 free.

PR #29 status:

- branch `feat/trusted-rdp-cert-lifecycle`;
- tested head `e914a0f45a6cc734d25b02340353fc06ace6c7c8`;
- CI #313 PASS Linux + Windows PowerShell 5.1;
- CI #316 PASS Linux + Windows PowerShell 5.1 after installer/uninstall wiring;
- server-side merge gate is satisfied.

Next:

- merge/reconcile PR #29;
- start **CERT-010** with a read-only Windows inventory on non-critical `SEC005 TEST` before any listener mutation;
- confirm current RDP listener thumbprint/hash type and TerminalServices CIM provider behavior;
- implement certificate delivery only over the existing pinned HTTPS + per-device bearer-auth channel;
- import the PFX into `Cert:\LocalMachine\My` without making the private key exportable;
- grant `NT AUTHORITY\NETWORK SERVICE` read access to the installed private key because Remote Desktop Services uses that identity;
- capture the previous listener hash and certificate before binding so rollback is deterministic;
- bind the trusted certificate only on `SEC005 TEST`, validate Microsoft Remote Desktop behavior, then test rollback;
- after Windows acceptance, implement renewal-driven rotation and expand carefully.

Architecture constraint: one independent Let’s Encrypt public-IP certificate per Windows device is not the scalable default because all devices share the same exact public-IP identifier set and duplicate/exact-set issuance limits apply. Use one short-lived lineage per Hermes server plus authenticated distribution/rotation.

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
