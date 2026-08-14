# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current published stable release until PR #35 is explicitly approved and merged. Historical tags are immutable.

## Immediate work

### 1. v1.3.0 release candidate

The next release is **v1.3.0**, not v1.2.2, because the cycle adds a new backward-compatible trusted RDP certificate capability across server, API and Windows lifecycle.

Draft PR #35 prepares:

- synchronized `1.3.0` version metadata;
- concise public release notes;
- full engineering history;
- changelog;
- post-release `UNRELEASED` reset;
- README/site/quickstart stable `v1.3.0` links;
- corrected release-process documentation.

Initial release head `13e2716276177849cb02a42864f824747537d88f`; CI #422 PASS.

Before publication:

1. reconcile the current context-only `main` checkpoint into PR #35;
2. rerun exact-head Linux + Windows PowerShell 5.1 CI;
3. keep PR #35 draft after PASS;
4. obtain explicit publication approval;
5. only then mark ready and merge with exact-head guard;
6. verify immutable `v1.3.0` tag, GitHub Release body and latest-release pointer.

Do not merge PR #35 automatically: merge triggers release publication.

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
