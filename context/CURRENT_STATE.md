# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` release PR merged, but automated tag selected an intermediate VERSION-changing commit rather than the complete release tree.
- Published `v1.2.0` tag is not rewritten; it remains historical evidence of the packaging error.
- PR #28: `v1.2.1` packaging hotfix merged after Linux + Windows PowerShell 5.1 CI PASS.
- `v1.2.1` tag points to exact commit `fd3c323da49f8994215d973e580d3949638b0f61` and contains consistent `VERSION`, package version, `pyproject.toml`, release notes and full rich product README.

## Runtime architecture

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd :7000
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent endpoint per device
```

Admin SSH remains independent from Hermes tunnel SSH. FRP is not active runtime. Each Windows client keeps its own local Ed25519 identity.

## Live deployment truth

- Production controller remains deployed from accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`.
- Release/documentation/context merges did not redeploy or mutate production runtime.
- SEC005 acceptance fixture remains healthy after updater/repair/RDP acceptance.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason:

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell/Sysnative;
- Telegram OFF/ON/RESTART and automatic dashboard refresh;
- Stage 3 security/device lifecycle acceptance;
- transactional server updater success/rollback;
- transactional Windows updater success/rollback;
- existing-device Repair success/rollback;
- Telegram Repair screen and deterministic new-code retry UX;
- Microsoft Defender real-time protection coexistence.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its deferred exact-Windows one-process observation; do not repeat the five-cycle stress test.

## Release automation follow-up

The release workflow root cause is confirmed: selecting `git log -1 -- VERSION` can tag an incomplete release tree. Prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b` changes tagging to exact validated workflow `HEAD` and adds a regression assertion. No PR is open yet.

## Current certificate state

The trusted-certificate track targets the **public IP**, not a new domain. Domain use is deferred because a domain alone does not change the certificate presented by the Windows RDP listener.

Live server evidence:

- Debian GNU/Linux 13 (trixie);
- Certbot installation completed successfully; current version **5.7.0**;
- CERT-003 external HTTP-01 reachability is **PASS**;
- UFW has an explicit `80/tcp` allow rule for ACME HTTP-01;
- a temporary HTTP listener on TCP 80 was reached successfully by five independent external probes, each returning HTTP `200`, with matching requests in the server access log;
- no public IP certificate has been issued yet;
- no Windows RDP certificate binding has been changed yet.

The target warning is controlled by the certificate presented by the Windows RDP listener. Installing a certificate only on the Hermes Linux/API endpoint is insufficient.

## Exact next step

Run **CERT-004**: stop the temporary CERT-003 Python listener, then perform a bounded Let’s Encrypt staging issuance for the public IP using Certbot standalone HTTP-01 and the required `shortlived` profile. Inspect the resulting staging certificate before any production issuance or Windows mutation.

First Windows acceptance target remains the non-critical `SEC005 TEST` device with rollback to its existing RDP listener certificate/state.
