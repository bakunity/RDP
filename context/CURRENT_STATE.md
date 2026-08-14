# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` release PR merged, but its tag captured an intermediate release tree; historical tag is not rewritten.
- PR #28: `v1.2.1` packaging hotfix merged and is the stable release.

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
- transactional server/Windows updater rollback acceptance;
- existing-device Repair acceptance;
- Microsoft Defender real-time protection coexistence.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its deferred exact-Windows one-process observation.

## Release automation follow-up

Prepared branch `fix/release-tag-head-v2` at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b` remains secondary to certificate work; no PR is open yet.

## Current certificate state

Trusted-certificate track targets the **public IP**, not a new domain.

Server-side evidence accepted:

- Certbot 5.7.0 under `/opt/certbot` with `/usr/local/bin/certbot` entry point;
- CERT-003 public HTTP-01 reachability: PASS; UFW allows `80/tcp`;
- CERT-004 staging public-IP issuance: PASS;
- CERT-005 key/fullchain inspection and renewal dry-run mechanics: PASS;
- CERT-006 real production Let’s Encrypt public-IP issuance: PASS;
- production issuer is Let’s Encrypt `YR1`; IP SAN, TLS Server Authentication EKU, RSA 2048, key match and local trust validation all confirmed;
- production renewal config uses standalone HTTP-01 and `shortlived`;
- TCP `80` is free;
- no Windows RDP certificate binding has been changed.

CERT-007 scheduler inventory is also complete. It found **no systemd timer, no matching service/unit and no cron entry invoking `certbot renew`**. Therefore automatic renewal is currently absent even though manual/dry-run renewal mechanics work. The current production certificate expires on 2026-08-20 21:54:07 UTC, so scheduler installation is a blocker before Windows rollout.

## Exact next step

Run **CERT-008**: install and validate a Hermes-owned systemd service/timer that periodically invokes normal `certbot renew` (never forced renewal), with persistent scheduling, randomized delay, logging and failure visibility. Then prove a bounded manual invocation succeeds without renewing early or leaving TCP `80` occupied.

After scheduler acceptance, design the successful-renewal deploy/rotation hook and the secure Windows certificate/private-key model, then integrate the lifecycle into Hermes RDP before first listener binding on `SEC005 TEST`.
