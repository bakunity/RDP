# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-15

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.3.0** is the current published stable release. Historical tags are immutable.

## PR #37 zero-config server onboarding

Runtime acceptance is complete. PR #37 is ready for review.

Remaining:

1. Wait for explicit user approval to merge.
2. Immediately before merge, verify the PR expected head is unchanged and required CI on that head is green.
3. Merge without rewriting historical release tags.

Do not repeat accepted PR #37 runtime checks unless a relevant code change creates regression risk.

## Deferred / non-blocking

### Natural certificate renewal observation

When the current short-lived production certificate renews naturally, confirm server non-secret state, automatic Windows rotation and a fresh trusted Microsoft RDP connection. Do not force production issuance solely for evidence.

### Optional residuals

- RL-006 remains PARTIAL only for an optional final one-process observation on the original exact Windows fixture; do not repeat prior reconnect stress.
- SEC-004 remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.

## After PR #37

Once PR #37 is merged, explicitly choose the next product phase rather than reopening accepted v1.3.0/PR #37 acceptance. The strongest planned direction remains separating Control Plane and Gateway/Data Plane boundaries before moving larger control-plane functionality toward Vercel.
