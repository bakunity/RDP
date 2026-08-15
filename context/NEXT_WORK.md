# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-15

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.3.0** is the current published stable release. Historical tags are immutable.

## Active workstream — PR #37 zero-config server onboarding

Core zero-config install and automatic trusted-certificate setup are live accepted on the Debian 13 Trixie fixture, including coexistence with an existing nginx listener on TCP 80.

Remaining before PR #37 can leave draft:

1. Send `/start` to the newly configured Telegram bot and confirm the normal Hermes dashboard opens for the securely claimed owner.
2. Clean the duplicate APT source entries already present on this fixture and confirm `apt-get update` no longer reports `configured multiple times`. The bootstrap cleanup is implemented with backup/revalidate/rollback and CI-covered; only bounded live fixture confirmation remains.
3. Checkpoint the two results into context/release draft and run final CI on the resulting exact head.
4. Mark PR #37 ready for review. Merge only after explicit user approval and with expected-head protection.

Do not repeat the already accepted core install, Telegram claim, nginx routing, staging/production certificate issuance or certificate renewal smoke unless a relevant code change regresses those paths.

## Deferred / non-blocking

### Natural certificate renewal observation

When the current short-lived production certificate renews naturally:

- confirm server non-secret state changes to the new certificate;
- confirm the Windows rotation worker detects the changed desired thumbprint;
- confirm automatic rotation succeeds without manual certificate setup;
- confirm a fresh Microsoft RDP connection remains trusted.

Do **not** force production issuance solely for this observation.

### Optional residuals

- RL-006 remains PARTIAL only for an optional final `HermesSshCount == 1` observation on the original exact Windows fixture after already-clean reconnect cycles. Do not repeat the stress test.
- SEC-004 remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.

## After PR #37

Once the zero-config onboarding workstream is merged, explicitly choose the next product phase rather than reopening accepted v1.3.0/PR #37 acceptance. The strongest planned direction remains separating Control Plane and Gateway/Data Plane boundaries before moving larger control-plane functionality toward Vercel.
