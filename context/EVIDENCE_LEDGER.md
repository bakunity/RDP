# Hermes RDP — Evidence Ledger

Updated: 2026-08-15

Purpose: compact current evidence index after the v1.3.0 release boundary. Detailed trusted-certificate/CERT-013 evidence is frozen in `context/archive/releases/v1.3.0-evidence.md`; full release history is in `docs/releases/history/v1.3.0-full.md`.

## Evidence levels

- **PASS / CONFIRMED** — runtime, CI, source or explicit user evidence exists.
- **PARTIAL PASS** — required subset is proven but an optional/original-fixture observation remains.
- **FAIL / CONFIRMED BUG** — failure was reproduced/established.
- **RESOLVED / LIVE-ACCEPTED** — confirmed bug has code, CI and bounded runtime acceptance.
- **IMPLEMENTED, NOT VALIDATED** — code exists but the environment-dependent behavior has not yet been accepted live.

A PASS proves the tested scenario/build boundary. Relevant later code changes create a new revalidation obligation.

## Current stable guarantees — v1.3.0

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| TR-001 | OpenSSH reverse RDP end-to-end | PASS | Real Windows clients paired; standard Microsoft RDP reached them through Hermes. |
| TR-002 | External-network RDP | PASS | Real external client connected through a public Hermes endpoint. |
| TR-003 | Windows reboot recovery | PASS | Tested Windows reboot recovered Agent/tunnel/RDP. |
| TR-004 | Linux reboot recovery | PASS | Hermes services/tunnels recovered after real Linux reboot. |
| TR-005 | Multi-device simultaneous operation | PASS | Independent endpoints/listeners worked concurrently. |
| TR-006 | One-device failure isolation | PASS | Scoped OFF/failure did not disrupt another device. |
| CT-001 | Telegram OFF/ON/RESTART | PASS | Control actions changed only the selected device and recovered transport. |
| WI-001 | Win10 x64 + x86 PowerShell / Sysnative OpenSSH | PASS | Real Win10 Pro 19045 under SysWOW64 PowerShell used native OpenSSH path successfully. |
| WI-002 | Windows Server 2019 | PASS | Fresh install/update preserved identity and real RDP worked. |
| UPD-001 | Transactional Linux updater | PASS | Immutable update creates backup and rolls back on bounded failure. |
| UPD-002 | Transactional Windows updater | PASS | Live success/forced-failure rollback preserved identity/task/tunnel. |
| REP-001 | Existing-device Repair | PASS | Missing runtime scaffolding recovery and rollback live accepted without re-pair/rekey. |
| DEF-001 | Microsoft Defender coexistence | PASS | Accepted runtime needs no Hermes exclusion or Defender disablement. |
| CERT-130 | Trusted public-IP RDP certificate lifecycle | PASS | Server issuance/renewal, authenticated Windows delivery, CUSTOM listener binding, automatic drift recovery and normal Windows lifecycle integration accepted through CERT-013. |

## v1.3.0 publication evidence

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| REL-130A | Final release candidate | PASS | PR #35 final head `74834bd741b5b8794a4d0277976ea3650e35f6c2`; CI #426 Linux full release checks + Windows PowerShell 5.1 PASS. |
| REL-130B | Release PR merge | PASS | PR #35 merged as `a51e942afbd17997a8100d554f8a0b2e50d4baa7`. |
| REL-130C | Automated publication workflow | PASS | `Publish release` workflow run #30 completed successfully, including release-tree validation, tag creation and GitHub Release publication. |
| REL-130D | Release tag provenance | PASS | Annotated tag `v1.3.0` points exactly to merge commit `a51e942afbd17997a8100d554f8a0b2e50d4baa7`. |
| REL-130E | GitHub Release / latest | PASS | `Hermes RDP v1.3.0` published as non-draft/non-prerelease; `releases/latest` resolves to `v1.3.0`. |

## PR #37 — zero-config server onboarding

Live fixture: Debian 13 Trixie on a fresh/new server. Public identifiers, Telegram numeric owner ID, bot token and one-time claim values are intentionally omitted.

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| ZC-001 | Stale Debian archive source recovery | RESOLVED / LIVE-ACCEPTED | Initial `apt-get update` failed because Trixie was pointed at `archive.debian.org`; bootstrap backed up sources, moved the known stale Debian URIs to current mirrors and `apt-get update` passed. |
| ZC-002 | Telegram bot validation and secure owner claim | RESOLVED / LIVE-ACCEPTED | `getMe` PASS, webhook-free PASS, exact private one-time `/claim` accepted only where actor ID equals chat ID; owner confirmed before permanent Hermes config. |
| ZC-003 | Immutable source archive resolution | RESOLVED / LIVE-ACCEPTED | Live failure exposed executable-mode mismatch; required server scripts now ship executable and exact source resolution passed. |
| ZC-004 | Zero-config core server install | PASS | Core install completed; dedicated Hermes sshd active, controller active and bootstrap reached `=== HERMES RDP READY ===`. |
| ZC-005 | Existing nginx on TCP 80 coexistence | RESOLVED / LIVE-ACCEPTED | nginx remained active; existing site configuration preserved; Hermes uses a dedicated IP-only ACME server block rather than stopping nginx. |
| ZC-006 | nginx ACME route/file mapping | RESOLVED / LIVE-ACCEPTED | Live diagnostic proved IP route selection and direct challenge `alias` both returned HTTP 200; previous `root + try_files` path was retired. |
| ZC-007 | nginx reload readiness | RESOLVED / LIVE-ACCEPTED | Manual probe exposed reload timing sensitivity; setup now uses bounded readiness retries before ACME. Code boundary `0aa6bed193abcd6ef60673304695e7565d697011`, CI #453 PASS. |
| ZC-008 | Let's Encrypt staging IP certificate via nginx webroot | PASS | Staging short-lived public-IP certificate issuance completed successfully on the live fixture. |
| ZC-009 | Let's Encrypt production IP certificate via nginx webroot | PASS | Production short-lived public-IP certificate issuance completed successfully on the live fixture. |
| ZC-010 | Hermes trusted certificate lifecycle after zero-config install | PASS | `renewal_timer=active`, `renewal_enabled=enabled`, `renewal_smoke=PASS_NOT_DUE`, `acme_mode=nginx-webroot`, `tcp80=NGINX_WEBROOT`, `package_helper=READY`, `certificate_state=READY`, `TRUSTED_RDP_CERT=PASS`. |
| ZC-011 | Exact duplicate APT source cleanup | IMPLEMENTED, NOT VALIDATED | Bootstrap removes only exact duplicate `deb`/`deb-src` entries after backup and re-validates APT with rollback on failure; CI-covered. Existing live fixture still needs bounded cleanup confirmation. |
| ZC-012 | Claimed-owner `/start` dashboard on this new server | PENDING | Final normal-user Telegram dashboard confirmation remains before PR closure. |

## Deferred / non-blocking observations

| ID | Scenario | Status | Boundary |
|---|---|---|---|
| CERT-NATURAL | Natural renewal-driven Windows rotation | PENDING / DEFERRED | Observe the next real renewal; do not force production issuance solely for evidence. |
| RL-006 | Final exact-Windows one-process observation | PARTIAL PASS | Optional original-fixture observation only; do not repeat prior reconnect stress. |
| SEC-004 | Revoked-credential fixture | FIXTURE-UNAVAILABLE | Do not reconstruct revoked credentials solely for artificial evidence. |

## Historical evidence

Detailed v1.3.0 certificate and lifecycle evidence, including intermediate confirmed bugs and their live-accepted fixes, is preserved in:

- `context/archive/releases/v1.3.0-evidence.md`;
- `docs/releases/history/v1.3.0-full.md`;
- Git history for PRs #29–#35.

Never convert an untested requirement to PASS merely because code exists. Never store secrets in evidence files.
