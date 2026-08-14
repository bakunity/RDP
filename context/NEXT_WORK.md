# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Do not rewrite historical tags.

## Immediate work

### 1. CERT-012 — automatic trusted RDP certificate rotation

Already complete:

- CERT-001 through CERT-011: PASS;
- PR #29 server certificate lifecycle merged/live accepted;
- PR #30 authenticated Windows certificate delivery/binding merged/live accepted;
- trusted → rollback → self-signed warning return → fixed reapply → trusted external connection sequence fully proven on `SEC005 TEST`;
- draft PR #31 automatic rotation core implemented outside the performance-sensitive main agent loop;
- PR #31 current immutable head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`;
- CI #344: Linux PASS + Windows PowerShell 5.1 PASS;
- CERT-012 server deploy PASS on that immutable head;
- server publishes only non-secret certificate status metadata and renewal refreshes that state;
- production certificate serial stayed unchanged during deploy/smoke.

Next bounded acceptance:

1. Install the separate SYSTEM rotation worker transactionally on `SEC005 TEST` from `79cab42d...`.
2. With current trusted binding, require `CERT_ROTATION=UNCHANGED`, task Running, and `CERT-012_SETUP=PASS`.
3. Create local drift with the already accepted self-signed rollback mechanism.
4. Do **not** manually reapply the trusted certificate; require the rotation worker to detect drift and restore CUSTOM trusted binding automatically.
5. Confirm one fresh Microsoft Remote Desktop connection is trusted again.
6. If green, mark PR #31 merge-ready and merge.
7. Later observe a natural renewal-driven thumbprint change; do not force unnecessary production issuance just to test rotation.
8. Wire the accepted rotation companion into normal fresh install / transactional update / repair if any lifecycle gap remains before the next release.

Architecture constraint: one short-lived public-IP lineage per Hermes server plus authenticated distribution/rotation. No duplicate independent public-IP certificate per Windows device by default.

### 2. Release automation hardening

- review/merge prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`;
- release workflow must tag the exact validated workflow HEAD;
- retain regression assertion;
- do not alter published `v1.2.0` or `v1.2.1` tags.

### 3. Post-certificate release/docs

After automatic rotation is accepted:

- document public-IP trusted RDP requirements and automatic renewal/rotation;
- decide next patch/minor release boundary;
- reconcile website/readme messaging;
- continue website v2 without reopening completed runtime tests.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.
