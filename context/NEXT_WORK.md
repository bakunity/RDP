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
- CERT-010 read-only `SEC005 TEST` Windows RDP certificate inventory: PASS; default self-signed baseline and rollback thumbprint confirmed, no mutation.

Active CERT-011 work:

- draft PR #30 `feat: add authenticated Windows RDP certificate rotation`;
- branch `feat/windows-rdp-cert-rotation`;
- tested head `af054274405c33849b8bbdee0a730320a8b5ab33`;
- authenticated device certificate-package endpoint implemented;
- bounded root PFX helper and exact sudoers permission implemented;
- Windows PowerShell 5.1 transactional sync/bind/rollback script implemented;
- server setup/updater/uninstall lifecycle implemented;
- CI #324 PASS: Linux full release checks + Windows PowerShell 5.1.

Next:

- deploy immutable PR #30 head to the current trusted-cert Linux host through the transactional server updater;
- verify `UPDATE=PASS`, controller/sshd health, helper/sudoers presence and no certificate-lineage mutation;
- run the immutable CERT-011 sync only on `SEC005 TEST`;
- require pinned authenticated package retrieval, non-exportable LocalMachine private key, NetworkService Read ACL, CUSTOM RDP hash type and TCP 3389 listener preservation;
- open a **new** Microsoft Remote Desktop connection through the Hermes endpoint and verify the intended trust/name warning is gone;
- preserve the old thumbprint/rollback data until real reconnect acceptance is complete;
- after bounded CERT-011 acceptance, integrate periodic certificate sync into the normal Hermes Windows agent so renewal-driven rotation is automatic;
- then validate one real renewal/rotation cycle before expanding to other Windows devices.

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
