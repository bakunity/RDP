# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Do not rewrite historical tags.

## Immediate work

### 1. Disposable fixture cleanup

PR #32 / CERT-013 is merged and fully live accepted.

Delete `CERT013 FRESH` in Telegram so its device token/SSH key are revoked and test port `53394` is freed. The local disposable VM client has already been successfully uninstalled.

### 2. Post-CERT-013 documentation/product reconciliation

The runtime now automatically manages trusted RDP certificate rotation through normal Fresh Install, Update and Repair, and removes the companion on Uninstall.

Audit and reconcile:

- README product/architecture/quick-start text;
- `docs/INSTALL_WINDOWS.md`;
- update/Repair/uninstall documentation;
- security/trusted-certificate explanation;
- validated scenarios/testing docs;
- website copy and architecture explanation.

Do not reopen already accepted runtime tests merely for documentation changes.

### 3. Next release boundary

Use `docs/releases/UNRELEASED.md` as the source of truth and decide whether the accumulated trusted-certificate + CERT-013 work should ship as the next patch or minor release.

Do not publish automatically. Before a release cut, prepare compact public release notes plus full engineering history according to `docs/releases/README.md`.

### 4. Natural renewal observation — deferred/non-blocking

When the current short-lived production certificate renews naturally:

- capture old/new server thumbprints;
- confirm server non-secret state refreshes;
- confirm Windows worker detects the changed thumbprint and rotates automatically;
- confirm fresh Microsoft RDP remains trusted.

Do **not** force unnecessary production issuance solely for this observation.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.