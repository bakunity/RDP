# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Use `v1.2.1` for new installs and updates; do not rewrite historical `v1.2.0`.

## Immediate work

### 1. Trusted RDP certificate on public IP

This is the active product stage. Domain introduction is deferred unless later required by certificate issuance/renewal or user-facing RDP behavior.

Already complete:

- CERT-001 server inventory: Debian 13; no Nginx; TCP `80/443` unused; Certbot initially absent.
- CERT-002 Certbot installation: `certbot 5.7.0` PASS.
- CERT-003 public HTTP-01 reachability: PASS; UFW explicitly allows `80/tcp`, and five independent external probes reached a temporary listener with HTTP `200` and matching server access-log entries.
- CERT-004 Let’s Encrypt staging public-IP issuance: PASS; critical IP SAN, RSA 2048, Server Authentication EKU, expected short-lived validity, staging CA issuer, and TCP 80 released after issuance.

Next:

- **CERT-005:** inspect the staging lineage/chain and safe renewal metadata and verify leaf/private-key consistency without exposing private-key material;
- after CERT-005, replace the staging lineage with one bounded production issuance and inspect the trusted production chain;
- remember the trust warning is produced by the Windows RDP listener certificate, not by HTTPS API TLS;
- design safe certificate/private-key delivery or issuance so secret material is not spread unnecessarily;
- design automated renewal before Windows deployment because public-IP certificates are short-lived and become renewal-eligible when about half of their <=10-day lifetime remains;
- bind/test first on non-critical `SEC005 TEST` and preserve its previous listener certificate/state as rollback;
- validate Microsoft Remote Desktop no longer reports the intended trust/name warning;
- only then expand to other Windows devices.

Do not mutate Windows/RDP until server-side production certificate issuance and renewal design are proven.

### 2. Release automation hardening

- review/merge prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`;
- release workflow must tag the exact validated workflow `HEAD`, not an earlier commit that happened to change `VERSION`;
- retain the regression assertion;
- do not alter existing published `v1.2.0` or `v1.2.1` tags.

### 3. Post-release docs / website

After certificate behavior is accepted:

- document public-IP trusted RDP certificate requirements and renewal;
- reconcile website messaging with `v1.2.1` and the full product README;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the five-cycle stress test.

## Context-system follow-up

Optional later: compact/reconcile `EVIDENCE_LEDGER.md` at the release boundary and add lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
