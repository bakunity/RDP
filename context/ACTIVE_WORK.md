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

User decision: **do not add a domain only for appearance**. Proceed with a certificate whose identity is the public IP. The certificate that matters for the Microsoft Remote Desktop warning must ultimately be presented by the **Windows RDP listener**, not merely installed on the Linux/API side.

### CERT-001 — server inventory — PASS

- Debian GNU/Linux 13 (trixie).
- Certbot was initially absent; Nginx absent; TCP `80/443` unused at the time of inventory.

### CERT-002 — Certbot install — PASS

- Certbot installed in an isolated Python environment under `/opt/certbot` with `/usr/local/bin/certbot` entry point.
- Live version: `certbot 5.7.0`.

### CERT-003 — external TCP 80 / HTTP-01 reachability — PASS

- UFW explicitly allows `80/tcp` for ACME HTTP-01.
- Five independent external probes reached a temporary listener and returned HTTP `200`; matching GETs appeared in the server access log.
- Do not repeat unless firewall/network state changes or ACME validation later contradicts it.

### CERT-004 — staging public-IP issuance — PASS

- Let’s Encrypt staging issuance succeeded with standalone HTTP-01 and `shortlived`.
- Leaf SAN contains the public IPv4 identifier; EKU is `TLS Web Server Authentication`; RSA 2048.

### CERT-005 — staging chain/key/renewal mechanics — PASS

- Certificate/private-key public keys match.
- Staging fullchain parsed correctly.
- `certbot renew --cert-name <public-ip> --dry-run --non-interactive` succeeded.
- Evidence boundary: renewal mechanics are proven; automatic scheduling was not yet verified.

### CERT-006 — production public-IP issuance — PASS

- Staging lineage had no external service references and was removed with `certbot delete`.
- Real Let’s Encrypt production issuance succeeded using the proven standalone HTTP-01 + `shortlived` + RSA 2048 settings.
- Production leaf issuer is Let’s Encrypt `YR1` and does not contain staging markers.
- SAN critically contains the public IPv4 identifier; EKU is `TLS Web Server Authentication`.
- Certificate/private-key public keys match (`PUBLIC_KEY_MATCH=PASS`).
- Local trust verification against the host CA store returned `OK`.
- Production renewal config points to `https://acme-v02.api.letsencrypt.org/directory`, uses `standalone`, RSA 2048 and `shortlived`.
- TCP `80` was free after issuance.
- Certificate is short-lived and requires reliable automated renewal/rotation before Windows deployment.
- No Windows RDP listener certificate state has been changed yet.

## Exact resume action

**CERT-007:** verify the real automatic-renewal scheduler on this pip/venv Certbot installation and, if absent, install a Hermes-owned systemd service/timer with safe cadence, locking, logging and failure visibility. Then prove it can invoke the existing production renewal path without leaving TCP `80` occupied.

After scheduler acceptance:

1. design renewal deploy/rotation hooks;
2. design secure Windows certificate/private-key delivery or a safer per-device key model;
3. integrate the proven certificate lifecycle into Hermes RDP rather than leaving it as manual operator commands;
4. validate first on non-critical `SEC005 TEST`, preserving the existing listener certificate/state as rollback;
5. only after Microsoft Remote Desktop trust acceptance expand to other devices.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
