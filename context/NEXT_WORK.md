# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Do not rewrite historical tags.

## Immediate work

### 1. CERT-013 final gate

PR #32 head: `29c19182ef99497b4cc314e3b4e9b6598ad95516`.
CI #363: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

Already live accepted on `SEC005 TEST`:

- transactional Update automatically manages certificate lifecycle while preserving identity, keys, known_hosts, Device ID, RDP port, main Agent/tunnel and trusted listener;
- targeted Repair recreates missing certificate rotation worker/task while preserving identity, port, tunnel and trusted RDP binding.

Do not repeat those tests without regression evidence. Do not uninstall `SEC005 TEST` for acceptance.

Remaining merge gate requires a separate disposable supported Windows test fixture:

1. fresh install from exact PR #32 head;
2. verify pairing, OpenSSH tunnel and external RDP;
3. verify certificate rotation worker/task are created automatically without manual certificate setup and run as LocalSystem SID `S-1-5-18`;
4. verify trusted CUSTOM listener and TCP 3389;
5. run normal uninstall;
6. verify both Hermes tasks/processes are removed and the active client directory is archived according to current uninstall behavior.

If no disposable fixture is available, keep PR #32 draft instead of risking the accepted `SEC005 TEST` state.

### 2. Natural renewal observation — deferred/non-blocking

When the current short-lived production certificate renews naturally:

- capture old/new server thumbprints;
- confirm server non-secret state refreshes;
- confirm Windows worker detects the changed thumbprint and rotates automatically;
- confirm fresh Microsoft RDP remains trusted.

Do **not** force unnecessary production issuance solely for this observation.

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
