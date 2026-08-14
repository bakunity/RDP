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
- No certificate has been issued yet.
- Windows/RDP listener has not been changed yet.

## Exact resume action

**CERT-003:** verify that the server's TCP `80` is reachable from the public Internet for ACME HTTP validation before requesting any certificate. Do not repeat CERT-001/CERT-002 unless there is evidence of regression.

After external reachability is confirmed:

1. perform a bounded staging/test issuance for the public IP using Certbot standalone;
2. inspect the resulting certificate identity/SAN and chain before using it;
3. design the secure Windows listener binding/renewal path;
4. validate first on the non-critical `SEC005 TEST` device while keeping the current self-signed RDP listener state as rollback;
5. only after user-facing Microsoft RDP trust acceptance expand to other devices.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
