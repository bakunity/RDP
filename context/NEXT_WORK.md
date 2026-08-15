# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-15

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.3.0** is the current published stable release. Historical tags are immutable.

## Active workstream — PR #37 zero-config server onboarding

Runtime acceptance is complete on the Debian 13 Trixie fixture, including semantic APT cleanup, masked Telegram token entry, secure owner claim, full clean-state reinstall, nginx coexistence and trusted RDP certificate lifecycle.

Remaining before merge:

1. Remove the temporary clean-reinstall acceptance helper from the branch.
2. Run final CI on the resulting exact head.
3. Mark PR #37 ready for review.
4. Merge only after explicit user approval and expected-head verification.

Do not repeat accepted zero-config runtime checks unless a relevant code change creates regression risk.

## Deferred / non-blocking

### Natural certificate renewal observation

When the current short-lived production certificate renews naturally, confirm server non-secret state, automatic Windows rotation and a fresh trusted Microsoft RDP connection. Do not force production issuance solely for evidence.

### Optional residuals

- RL-006 remains PARTIAL only for an optional final one-process observation on the original exact Windows fixture; do not repeat prior reconnect stress.
- SEC-004 remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.

## After PR #37

Once PR #37 is merged, explicitly choose the next product phase rather than reopening accepted v1.3.0/PR #37 acceptance. The strongest planned direction remains separating Control Plane and Gateway/Data Plane boundaries before moving larger control-plane functionality toward Vercel.
