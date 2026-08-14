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
- `v1.2.1` annotated tag points to exact commit `fd3c323da49f8994215d973e580d3949638b0f61` and contains synchronized VERSION/package metadata plus the full product README with badges, architecture, quick start, update/repair and security sections.
- GitHub Release `v1.2.1` published successfully and is the release to use for installs/updates.

## Deployment truth

- Live Linux controller/app remains deployed from accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`; release publication itself did not change production runtime.
- `SEC005 TEST` remains healthy after updater, repair and Microsoft RDP acceptance.
- Do not repeat completed stabilization/live acceptance without a concrete regression reason.

## Release automation follow-up

Confirmed packaging root cause from `v1.2.0`: `.github/workflows/release.yml` selected the last commit that changed `VERSION`, which can tag an incomplete release tree.

Prepared branch `fix/release-tag-head-v2` changes the release SHA to the exact validated workflow `HEAD` and adds a regression assertion. Current prepared branch head: `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`. No PR was successfully opened yet; this is secondary to the current certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: **do not add a domain only for appearance**. Proceed with a certificate whose identity is the public IP, because a domain by itself does not remove the Microsoft Remote Desktop warning. The certificate that matters for that warning must ultimately be presented by the **Windows RDP listener**, not merely installed on the Linux/API side.

### CERT-001 — server inventory — PASS

Read-only live inventory on the certificate host:

- OS: Debian GNU/Linux 13 (trixie);
- Certbot was not installed yet;
- Nginx absent;
- no listeners on TCP `80` or `443` at the time of the check.

### CERT-002 — Certbot install — PASS

- Certbot installed in an isolated Python environment under `/opt/certbot` with `/usr/local/bin/certbot` entry point.
- Live version output: `certbot 5.7.0`.
- No certificate had been issued at this stage.
- Windows/RDP listener had not been changed.

### CERT-003 — external TCP 80 / HTTP-01 reachability — PASS

- UFW is active with default incoming deny; explicit `80/tcp` ACME HTTP-01 allow rule was added.
- Temporary standalone HTTP listener bound to `0.0.0.0:80` and served a unique test response locally.
- Five independent external probes from different regions all reached the public IPv4 endpoint and returned HTTP `200`.
- Server access log independently recorded all five external GET requests.
- This proves the public path Internet -> TCP 80 -> host firewall -> local HTTP listener for HTTP-01 validation.
- Do not repeat CERT-003 unless firewall/network state changes or ACME validation later contradicts it.

### CERT-004 — Let’s Encrypt staging IP issuance — PASS

- Temporary CERT-003 listener was removed before issuance and TCP `80` was free for Certbot standalone.
- Certbot standalone + HTTP-01 successfully obtained a Let’s Encrypt staging certificate for the public IPv4 identity using the `shortlived` profile.
- Certificate lineage was created under `/etc/letsencrypt/live/<public-ip>/`.
- Leaf certificate identity is carried in a critical Subject Alternative Name as an IP Address.
- Key type: RSA 2048.
- Extended Key Usage: TLS Web Server Authentication.
- Validity matches the short-lived IP-certificate model (about 160 hours / just over six days).
- Issuer is a Let’s Encrypt staging CA, so the current artifact is intentionally not publicly trusted and must not be deployed to Windows RDP.
- TCP `80` was free again after Certbot completed.
- Windows/RDP listener state remains unchanged.

## Exact resume action

**CERT-005:** inspect the staging lineage/chain and renewal metadata without exposing private-key material, confirm certificate/private-key consistency by public-key comparison, and verify that standalone HTTP-01 + `shortlived` are preserved for future renewal. Do not mutate Windows/RDP yet.

After CERT-005 passes:

1. remove/replace the staging lineage cleanly and perform one bounded **production** issuance for the public IP;
2. inspect the production SAN, issuer/chain, EKU and validity;
3. design automated renewal because IP certificates are short-lived and standalone must be able to bind TCP `80`;
4. design secure certificate/private-key delivery to the Windows RDP listener;
5. validate first on the non-critical `SEC005 TEST` device while keeping the current self-signed RDP listener state as rollback;
6. only after user-facing Microsoft RDP trust acceptance expand to other devices.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
