# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** remains the published stable release until draft PR #35 is explicitly approved and merged. Historical tags are immutable.

## Immediate work

### 1. v1.3.0 publication decision

The next release is **v1.3.0**, not v1.2.2, because the cycle adds a new backward-compatible trusted RDP certificate capability across server, API and Windows lifecycle.

Draft PR #35 contains:

- synchronized `1.3.0` version metadata;
- concise public release notes;
- full engineering history;
- changelog;
- post-release `UNRELEASED` reset;
- README/site/quickstart stable `v1.3.0` links;
- corrected release-process documentation.

CI evidence:

- atomic release tree head `13e2716276177849cb02a42864f824747537d88f`: CI #422 PASS;
- reconciled pre-approval head `8555aa3977f0f954f11fdf944a5ebedeeb3d815c`: CI #424 PASS.

PR #35 remains draft intentionally.

Do not merge automatically. Merge changes `VERSION` in `main` and triggers immutable tag + GitHub Release publication.

On explicit approval:

1. reconcile the latest context-only `main` checkpoint into PR #35 one final time;
2. rerun exact-head Linux + Windows PowerShell 5.1 CI;
3. mark ready only after PASS;
4. merge with exact-head guard;
5. verify `v1.3.0` tag, GitHub Release body and latest-release pointer.

### 2. Natural renewal observation — deferred/non-blocking

When the current short-lived production certificate renews naturally:

- capture old/new server thumbprints;
- confirm server non-secret state refreshes;
- confirm Windows worker detects the changed thumbprint and rotates automatically;
- confirm fresh Microsoft RDP remains trusted.

Do **not** force unnecessary production issuance solely for this observation.

## Optional deferred items

- RL-006 remains PARTIAL only for an optional final Windows one-process observation on the original exact fixture after already-clean reconnect cycles. Do not repeat the stress test.
- SEC-004 remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.
