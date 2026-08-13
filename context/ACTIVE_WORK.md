# Hermes RDP — Active Work

Updated: 2026-08-13

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #19 through PR #25: merged / runtime accepted.
- PR #26 documentation reconciliation: merged.
- PR #27 `v1.2.0`: merged, but its automated tag resolved to an intermediate VERSION-changing commit rather than the complete release tree.
- `v1.2.0` tag is intentionally not rewritten after publication.
- PR #28 `v1.2.1` packaging hotfix: merged; CI #285 Linux + Windows PowerShell 5.1 PASS.
- `v1.2.1` annotated tag points to exact commit `fd3c323da49f8994215d973e580d3949638b0f61` and contains synchronized VERSION/package metadata plus the full product README.
- GitHub Release `v1.2.1` published successfully.

## Deployment truth

- Live Linux controller/app remains deployed from accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`; release publication itself did not change production runtime.
- `SEC005 TEST` remains healthy after updater, repair and Microsoft RDP acceptance.

## Completed stabilization scope

- Device/security acceptance: COMPLETE except SEC-004 remains fixture-unavailable by design.
- Server + Windows transactional updater: COMPLETE / LIVE-ACCEPTED.
- Existing-device Windows Repair engine: COMPLETE / LIVE-ACCEPTED.
- Telegram Repair + deterministic new pairing-code UX: COMPLETE / LIVE-ACCEPTED.
- Full public README restored with release/CI/license/OpenSSH/Windows/Linux badges, product architecture, quick start, update/repair and security sections.
- Do not repeat completed live tests without a concrete regression reason.

## Release automation follow-up

Root cause found during `v1.2.0`: `.github/workflows/release.yml` historically selected the last commit that changed `VERSION`, which is unsafe when release metadata is committed in multiple steps.

A prepared follow-up branch `fix/release-tag-head-v2` changes release tagging to the exact validated `HEAD` and adds a regression assertion. It is not yet merged.

## Exact next product track

Proceed to **RDP trusted-certificate / domain architecture** after release housekeeping. HTTPS API TLS and the Windows RDP listener certificate are separate layers; the RDP listener must receive a hostname-matching trusted certificate to remove the Microsoft Remote Desktop trust warning.

## Context rule

Checkpoint meaningful outcomes, not raw transcripts. Never store pairing codes, API tokens, private keys or ready-to-use secret material in context.
