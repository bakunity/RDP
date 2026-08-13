# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-13

For exact immediate action read `ACTIVE_WORK.md`. This file is the remaining product-level queue; completed work is removed rather than kept for history.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. It contains the live-accepted stabilization runtime and the corrected full release tree/product README. Use `v1.2.1` for new installs and updates; do not rewrite historical `v1.2.0`.

## Immediate work

### 1. RDP trusted certificate / domain

This is the next product stage.

- choose and document the hostname scheme used by Microsoft Remote Desktop;
- keep HTTPS API TLS and Windows RDP listener TLS as separate certificate bindings;
- issue a hostname-matching Server Authentication certificate for the Windows RDP listener;
- prefer locally generated per-device private keys rather than copying one shared wildcard private key to all Windows clients;
- bind the resulting certificate to the RDP listener and ensure the listener service can read its private key;
- design renewal and rollback before automating certificate rotation;
- validate one non-critical Windows device first, then expand;
- keep current self-signed listener behavior as a safe fallback until the trusted flow is accepted.

### 2. Release automation hardening

- merge/review the prepared `fix/release-tag-head-v2` change when connector policy allows;
- release workflow must tag the exact validated release `HEAD`, not an earlier commit that happened to change `VERSION`;
- retain a regression test for this invariant;
- do not alter existing published `v1.2.0` or `v1.2.1` tags.

### 3. Post-release docs / website

After certificate architecture is decided:

- document trusted RDP certificates and hostname requirements;
- reconcile website messaging with `v1.2.1` and the full product README;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the five-cycle stress test.

## Context-system follow-up

Optional later: lightweight context-hygiene/lint checks for required files, freshness, size and contradictory status patterns.
