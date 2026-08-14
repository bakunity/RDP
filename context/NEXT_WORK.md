# Hermes RDP — Next Work / Goal Vector

Updated: 2026-08-14

For exact immediate action read `ACTIVE_WORK.md`. This file contains only remaining product-level work.

## North-star goal

Ship a stable self-hosted product where a user can install Hermes on Debian/Ubuntu, add supported Windows devices through Telegram, receive persistent per-device endpoints, connect with standard Microsoft Remote Desktop, trust every displayed status, survive reboots/network failures automatically, and update safely without losing access.

## Stable release

**Hermes RDP v1.2.1** is the current stable published release. Do not rewrite historical tags.

## Immediate work

### 1. Merge CERT-013

PR #32 has completed all bounded live acceptance.

Accepted product/test code head: `e11cf89ed26d551ca92b4010034d6e6792a9266b`.
Reconcile CI #381: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

Accepted live paths:

- transactional Update on `SEC005 TEST`;
- targeted Repair on `SEC005 TEST`;
- clean Fresh Install on disposable Win10 Pro 19045 x64 fixture `DESKTOP-T9N368F` with Defender enabled;
- real external Microsoft RDP to `150.241.94.110:53394` with trusted certificate/no self-signed warning;
- normal Uninstall removing both Hermes tasks/processes and archiving/removing the active client directory while Defender stayed enabled.

Do not repeat any of those tests without concrete regression evidence.

Next actions:

1. wait for CI on evidence-only PR head;
2. mark PR #32 ready and merge with exact-head guard;
3. delete the disposable `CERT013 FRESH` Telegram registration so its API token/SSH key are revoked and port `53394` is freed;
4. checkpoint merged SHA and move to the next product gap.

### 2. Natural renewal observation — deferred/non-blocking

When the current short-lived production certificate renews naturally:

- capture old/new server thumbprints;
- confirm server non-secret state refreshes;
- confirm Windows worker detects the changed thumbprint and rotates automatically;
- confirm fresh Microsoft RDP remains trusted.

Do **not** force unnecessary production issuance solely for this observation.

### 3. Next release / docs

Release-process hardening is already complete: exact validated HEAD tagging, compact public release notes, long-form history files and rolling `UNRELEASED.md` are in `main`.

After CERT-013 merge:

- reconcile README/website/docs with the now-shipped automatic certificate lifecycle;
- decide next patch/minor release boundary from `UNRELEASED.md`;
- continue website v2 without reopening completed runtime acceptance.

## Optional deferred item

RL-006 remains PARTIAL PASS only because the exact original Windows machine did not receive the final lightweight `HermesSshCount == 1` observation after five already-clean server-side reconnect cycles. If that exact fixture is later identified, collect only that one count. Do not repeat the stress test.
