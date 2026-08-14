# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Do not rewrite historical tags.

## Immediate work

### 1. CERT-013 — integrate trusted certificate rotation into normal Windows lifecycle

CERT-001 through CERT-012 bounded acceptance is complete. PR #31 automatic rotation is merged as `bd25db552aae8303356953fe2807a7bd855cba95`.

Remaining product gap: the accepted rotation worker currently has a dedicated setup script; normal users should not need to run that step separately.

Implement and test:

1. fresh install installs/starts the rotation companion after device config exists;
2. transactional update stages/parses/updates worker + sync companion and restores them/task on failure;
3. Repair restores missing/disabled/broken rotation task/files without re-pairing or key rotation;
4. uninstall removes Hermes-owned rotation task/files cleanly;
5. preserve LocalSystem SID validation, mutex ACL behavior and immutable repository SHA;
6. preserve Windows PowerShell 5.1 and Win10 x64 + x86 PowerShell/Sysnative compatibility;
7. keep certificate work outside the 3-second main agent loop;
8. add CI regression coverage and then perform bounded live acceptance on `SEC005 TEST`.

Do not reopen already accepted certificate issuance/binding/rollback/drift tests unless lifecycle integration changes those exact paths.

### 2. Natural renewal observation — deferred/non-blocking

When the existing short-lived production certificate renews naturally:

- capture old/new server thumbprints;
- confirm server non-secret state refreshes;
- confirm Windows worker detects the changed thumbprint and rotates automatically;
- confirm fresh Microsoft RDP remains trusted.

Do **not** force unnecessary production issuance solely to satisfy this observation.

### 3. Release automation hardening

- review/merge prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`;
- release workflow must tag the exact validated workflow HEAD;
- retain regression assertion;
- do not alter published `v1.2.0` or `v1.2.1` tags.

### 4. Next release / docs

After CERT-013 lifecycle integration:

- document public-IP trusted RDP requirements, automatic renewal and Windows rotation;
- decide next patch/minor release boundary;
- reconcile README/website with the shipped lifecycle;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.
