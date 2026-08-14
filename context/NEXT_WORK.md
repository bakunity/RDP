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
- CERT-003 public HTTP-01 reachability: PASS.
- CERT-004 Let’s Encrypt staging public-IP issuance: PASS.
- CERT-005 key/fullchain/renewal dry-run: PASS.
- CERT-006 production public-IP issuance: PASS.
- CERT-007 scheduler inventory: PASS; missing scheduler gap confirmed.
- CERT-008 Hermes-owned automatic renewal: live PASS.
- CERT-009 productized server lifecycle: live PASS and PR #29 merged as `33c7b6ac6e5a6fb732963988c4734a8a7ef8ec5e`.
- CERT-010 read-only `SEC005 TEST` Windows RDP certificate inventory: PASS.

CERT-011 partial acceptance complete:

- draft PR #30 `feat: add authenticated Windows RDP certificate rotation`;
- tested/deployed head `af054274405c33849b8bbdee0a730320a8b5ab33`;
- CI #324 PASS: Linux full release checks + Windows PowerShell 5.1;
- transactional server updater deploy: PASS;
- current trusted certificate serial unchanged during deploy;
- package helper/sudoers and real `hermes-rdp -> sudo` helper execution: PASS;
- controller, sshd and renewal timer active; TCP 80 free;
- `SEC005 TEST` authenticated package retrieval: PASS;
- PFX import into `LocalMachine\My`: PASS;
- imported CNG private key verified non-exportable;
- `NETWORK SERVICE` Read ACL: PASS;
- RDP listener switched to CUSTOM trusted-certificate thumbprint;
- TCP 3389 remained listening;
- previous self-signed thumbprint and rollback data preserved.

Next:

- open a **new** Microsoft Remote Desktop connection from a separate client through the normal Hermes public endpoint for `SEC005 TEST`;
- verify connection succeeds and the old certificate trust/identity warning is absent;
- if a warning remains, capture its exact text/screenshot rather than changing more state;
- after external PASS, execute the explicit Hermes rollback once, confirm the old binding returns, then reapply the trusted binding and reconnect again;
- after bounded bind/rollback acceptance, integrate periodic certificate sync into the normal Hermes Windows agent;
- trigger sync only when the server certificate thumbprint changes or local binding drifts;
- validate one actual renewal-driven rotation cycle before rollout to other devices;
- then make trusted certificate delivery/rotation a polished normal Hermes installation/update feature and merge PR #30.

Architecture constraint: one independent Let’s Encrypt public-IP certificate per Windows device is not the scalable default because all devices share the same exact public-IP identifier set and CA issuance limits apply. Use one short-lived lineage per Hermes server plus authenticated distribution/rotation.

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
