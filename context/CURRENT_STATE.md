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
- Release/documentation/context changes did not redeploy or mutate production runtime.
- `SEC005 TEST` remains healthy after updater/repair/RDP acceptance.

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

Prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b` changes release tagging to exact validated workflow `HEAD` and adds a regression assertion. No PR is open yet; certificate work remains higher priority.

## Current certificate state

The trusted-certificate track targets the **public IP**, not a new domain.

Server-side certificate evidence now accepted:

- Debian GNU/Linux 13 (trixie);
- Certbot 5.7.0 installed under `/opt/certbot` with `/usr/local/bin/certbot` entry point;
- CERT-003 public HTTP-01 reachability: PASS; UFW explicitly allows `80/tcp`;
- CERT-004 staging public-IP issuance: PASS;
- CERT-005 certificate/key/fullchain inspection and renewal dry-run mechanics: PASS;
- CERT-006 real Let’s Encrypt production public-IP issuance: PASS;
- production SAN contains the public IPv4 identifier;
- EKU is TLS Web Server Authentication;
- issuer is production Let’s Encrypt `YR1`, not staging;
- certificate/private-key public keys match;
- local CA trust verification returns `OK`;
- production renewal config uses standalone HTTP-01, RSA 2048 and the `shortlived` profile;
- TCP `80` is free after issuance;
- no Windows RDP certificate binding has been changed yet.

The certificate is intentionally short-lived, so reliable automatic renewal and deploy/rotation are mandatory before user-facing rollout.

## Exact next step

Run **CERT-007**: inspect whether this pip/venv Certbot installation already has a real systemd/cron renewal scheduler. If not, install a Hermes-owned systemd service/timer, then verify its exact command, next-run state, logging and safe interaction with standalone TCP `80`.

After that, design the secure Windows certificate/key model and integrate the proven certificate lifecycle into Hermes RDP before first binding on `SEC005 TEST`.
