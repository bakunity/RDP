# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.3.0** is the current published stable release. Historical tags are immutable.

## Remaining work

### 1. Natural certificate renewal observation — deferred/non-blocking

When the current short-lived production certificate renews naturally:

- confirm server non-secret state changes to the new certificate;
- confirm the Windows rotation worker detects the changed desired thumbprint;
- confirm automatic rotation succeeds without manual certificate setup;
- confirm a fresh Microsoft RDP connection remains trusted.

Do **not** force production issuance solely for this observation.

### 2. Next product workstream

No v1.3.0 release blocker or unfinished lifecycle stage remains. Select the next product feature/phase explicitly before creating a new branch. Do not repeat accepted v1.3.0 runtime tests unless a relevant change creates regression risk.

## Optional deferred items

- RL-006 remains PARTIAL only for an optional final `HermesSshCount == 1` observation on the original exact Windows fixture after already-clean reconnect cycles. Do not repeat the stress test.
- SEC-004 remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.
