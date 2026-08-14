# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #19 through PR #25: merged / runtime accepted.
- PR #26 documentation reconciliation: merged.
- PR #27 `v1.2.0`: merged, but its automated tag resolved to an intermediate VERSION-changing commit rather than the complete release tree.
- `v1.2.0` tag is intentionally not rewritten after publication.
- PR #28 `v1.2.1` packaging hotfix: merged; Linux + Windows PowerShell 5.1 CI PASS.
- `v1.2.1` annotated tag points to exact commit `fd3c323da49f8994215d973e580d3949638b0f61` and is the release to use for installs/updates.

## Deployment truth

- Live Linux controller/app remains deployed from accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`; release/context changes did not redeploy production runtime.
- `SEC005 TEST` remains healthy after updater, repair and Microsoft RDP acceptance.
- Do not repeat completed stabilization/live acceptance without a concrete regression reason.

## Release automation follow-up

Prepared branch `fix/release-tag-head-v2` remains at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`; no PR is open yet. This remains secondary to the current certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: **do not add a domain only for appearance**. Proceed with a certificate whose identity is the public IP. The certificate relevant to the Microsoft Remote Desktop warning must ultimately be presented by the **Windows RDP listener**, not merely installed on Linux/API.

### CERT-001 — server inventory — PASS

- Debian GNU/Linux 13 (trixie).
- Certbot initially absent; Nginx absent; TCP `80/443` unused at inventory time.

### CERT-002 — Certbot install — PASS

- Certbot installed under `/opt/certbot`; `/usr/local/bin/certbot` entry point.
- Live version: `certbot 5.7.0`.

### CERT-003 — external TCP 80 / HTTP-01 reachability — PASS

- UFW explicitly allows `80/tcp` for ACME HTTP-01.
- Five independent external probes returned HTTP `200` from a temporary listener with matching server access-log GETs.

### CERT-004 — staging public-IP issuance — PASS

- Let’s Encrypt staging issuance succeeded with standalone HTTP-01 + `shortlived`.
- Critical SAN contains the public IPv4 identifier; EKU is TLS Web Server Authentication; RSA 2048.

### CERT-005 — staging chain/key/renewal mechanics — PASS

- Certificate/private-key public keys match.
- Fullchain parsed correctly.
- `certbot renew --cert-name <public-ip> --dry-run --non-interactive` succeeded.

### CERT-006 — production public-IP issuance — PASS

- Staging lineage safely removed with `certbot delete` after confirming no external service references.
- Production Let’s Encrypt issuance succeeded using standalone HTTP-01 + `shortlived` + RSA 2048.
- Production issuer is Let’s Encrypt `YR1`; critical SAN contains the public IPv4 identifier; EKU is TLS Web Server Authentication.
- Certificate/private-key public keys match; local trust verification returned `OK`.
- Production renewal config uses production ACME, standalone, RSA 2048 and `shortlived`.
- TCP `80` was free after issuance.
- No Windows RDP listener certificate state has been changed yet.

### CERT-007 — automatic-renewal scheduler inventory — PASS / GAP CONFIRMED

Read-only live inventory proved:

- Certbot path: `/usr/local/bin/certbot` -> `/opt/certbot/bin/certbot`;
- no matching systemd timer exists;
- no matching systemd service/unit exists;
- no `certbot renew` command exists in systemd units;
- no `certbot renew` command exists in cron;
- TCP `80` is currently free;
- production certificate remains valid through 2026-08-20 21:54:07 UTC.

Therefore renewal **mechanics** are proven, but automatic renewal is not configured. This is a blocker before Windows rollout because the public-IP certificate is short-lived.

## Exact resume action

**CERT-008:** install a Hermes-owned systemd renewal service/timer for this validated Certbot lineage, using periodic `certbot renew`, persistent scheduling, randomized delay, explicit logging/failure visibility and no forced renewal. Then validate unit syntax/state, next-run scheduling and a bounded manual service invocation without leaving TCP `80` occupied.

After scheduler acceptance:

1. design a deploy/rotation hook that runs only after successful renewal;
2. design the secure Windows certificate/private-key model;
3. integrate ACME install/issuance/renewal/rotation into Hermes RDP rather than leaving manual operator commands;
4. validate first on non-critical `SEC005 TEST`, preserving its existing listener certificate/state as rollback;
5. only after Microsoft Remote Desktop trust acceptance expand to other devices.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
