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

- CERT-001 through CERT-010: PASS.
- PR #29 server certificate lifecycle: merged/live accepted.
- CERT-011 core trusted binding: PASS on `SEC005 TEST`.
- Fresh Microsoft Remote Desktop connection through Hermes accepted the production Let’s Encrypt public-IP certificate and reported the server certificate as verified.

PR #30 current state:

- draft `feat: add authenticated Windows RDP certificate rotation`;
- current head `83e1b0b5d89b2728646a8eb518026ba9d1cf575a`;
- CI #324 initial implementation: Linux PASS + Windows PowerShell 5.1 PASS;
- live server deploy of initial head: PASS;
- Windows authenticated package, non-exportable CNG key, NetworkService Read, CUSTOM binding and 3389 listener: PASS;
- external trusted Microsoft RDP connection: PASS;
- first rollback attempt exposed confirmed default-self-signed restoration bug;
- live root cause: default self-signed is hash type `1` with no explicit `SSLCertificateSHA1Hash`, so it must be restored by removing the custom registry binding rather than setting its thumbprint as CUSTOM;
- corrected manual rollback: PASS; exact original self-signed thumbprint/hash type restored and TCP 3389 remained listening;
- PR fix uses type-aware rollback for explicit and automatic failure paths;
- CI #333 on fixed head: Linux PASS + Windows PowerShell 5.1 PASS.

Next:

1. While `SEC005 TEST` is currently on restored default self-signed state, open one fresh external RDP connection and confirm access still works; the original certificate warning is expected.
2. Reapply trusted binding using fixed head `83e1b0b...`.
3. Confirm local CUSTOM binding / TCP 3389 and one fresh external trusted reconnect.
4. Mark PR #30 merge-ready and merge after those bounded checks.
5. Integrate periodic certificate sync into the normal Hermes Windows agent, triggered only when the server certificate thumbprint changes or local binding drifts.
6. Validate one real renewal-driven rotation cycle before expanding to other devices.
7. Then make trusted certificate delivery/rotation a polished normal Hermes installation/update feature.

Architecture constraint: use one short-lived public-IP lineage per Hermes server plus authenticated distribution/rotation; independent duplicate public-IP certificates per Windows device are not the scalable default.

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
