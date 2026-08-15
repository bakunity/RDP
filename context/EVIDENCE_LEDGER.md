# Hermes RDP — Evidence Ledger

Updated: 2026-08-15

Purpose: compact current evidence index after the v1.3.0 release boundary. Detailed v1.3.0 certificate evidence remains frozen in `context/archive/releases/v1.3.0-evidence.md` and `docs/releases/history/v1.3.0-full.md`.

## Evidence levels

- **PASS / CONFIRMED** — runtime, CI, source or explicit user evidence exists.
- **PARTIAL PASS** — required subset is proven but an optional observation remains.
- **FAIL / CONFIRMED BUG** — failure was reproduced/established.
- **RESOLVED / LIVE-ACCEPTED** — confirmed bug has code, CI and bounded runtime acceptance.
- **IMPLEMENTED, NOT VALIDATED** — code exists but environment-dependent behavior lacks live acceptance.

A PASS proves the tested scenario/build boundary. Relevant later changes create a new revalidation obligation.

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
| WI-001 | Win10 x64 + x86 PowerShell / Sysnative OpenSSH | PASS | Real Win10 Pro 19045 under SysWOW64 PowerShell used native OpenSSH successfully. |
| WI-002 | Windows Server 2019 | PASS | Fresh install/update preserved identity and real RDP worked. |
| UPD-001 | Transactional Linux updater | PASS | Immutable update creates backup and rolls back on bounded failure. |
| UPD-002 | Transactional Windows updater | PASS | Live success/forced-failure rollback preserved identity/task/tunnel. |
| REP-001 | Existing-device Repair | PASS | Runtime scaffolding recovery and rollback accepted without re-pair/rekey. |
| DEF-001 | Microsoft Defender coexistence | PASS | Accepted runtime requires no Hermes exclusion or Defender disablement. |
| CERT-130 | Trusted public-IP RDP certificate lifecycle | PASS | Server issuance/renewal, authenticated Windows delivery, listener binding, drift recovery and lifecycle integration accepted through CERT-013. |

## PR #37 — zero-config server onboarding

Live fixture: Debian 13 Trixie. Public identifiers, Telegram numeric owner ID, bot token and one-time claim values are intentionally omitted.

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| ZC-001 | Stale Debian archive source recovery | RESOLVED / LIVE-ACCEPTED | Initial APT failure from stale archive URI was backed up, rewritten to current Debian mirrors and revalidated. |
| ZC-002 | Telegram bot validation and secure owner claim | RESOLVED / LIVE-ACCEPTED | `getMe` PASS, webhook-free PASS, private one-time owner claim accepted before permanent Hermes config. |
| ZC-003 | Immutable source archive resolution | RESOLVED / LIVE-ACCEPTED | Executable-mode mismatch was found live, fixed, regression-tested and exact source resolution passed. |
| ZC-004 | Zero-config core server install | PASS | Dedicated Hermes sshd and controller active; bootstrap reached `=== HERMES RDP READY ===`. |
| ZC-005 | Existing nginx on TCP 80 coexistence | RESOLVED / LIVE-ACCEPTED | Existing nginx/site remained active; Hermes uses a dedicated IP-only ACME route. |
| ZC-006 | nginx ACME route/file mapping | RESOLVED / LIVE-ACCEPTED | IP route selection and direct challenge `alias` returned HTTP 200; failing `root + try_files` path retired. |
| ZC-007 | nginx reload readiness | RESOLVED / LIVE-ACCEPTED | Reload timing sensitivity resolved with bounded readiness retries. |
| ZC-008 | Let's Encrypt staging IP certificate via nginx webroot | PASS | Staging short-lived public-IP issuance completed successfully. |
| ZC-009 | Let's Encrypt production IP certificate via nginx webroot | PASS | Production short-lived public-IP issuance completed successfully. |
| ZC-010 | Hermes trusted certificate lifecycle | PASS | Renewal timer active/enabled, smoke `PASS_NOT_DUE`, nginx-webroot mode, package/state helpers ready, `TRUSTED_RDP_CERT=PASS`. |
| ZC-011 | Overlapping APT source component normalization | RESOLVED / LIVE-ACCEPTED | First exact-line cleanup failed safely and rolled back. Root cause was overlapping component sets for the same type + URI + suite. Semantic component-union normalization then let the clean-reinstall flow proceed; subsequent exact-head install reported clean APT repositories. |
| ZC-012 | Claimed-owner `/start` dashboard | PASS | Normal Hermes dashboard confirmed working for the claimed owner. |
| ZC-013 | Masked Telegram token entry | RESOLVED / LIVE-ACCEPTED | Live install displayed only `*` characters while token validation succeeded; token value remained hidden. Empty/invalid bounded retry is regression-tested but was not separately fault-injected after the fix. |
| ZC-014 | Full clean-state reinstall | PASS | Hermes config/data/runtime identities were purged for acceptance; exact head `056bf7473ff851157f4c749f233fb0fb8b57a133` then installed successfully to READY with sshd/controller and trusted certificate lifecycle active. |
| ZC-015 | Interruption during owner-claim stage | PASS | Terminal was closed while waiting for claim after clean purge. Because owner claim precedes core mutation, no partial Hermes core remained; rerunning the normal installer succeeded. |
| ZC-016 | Exact-head CI before final context cleanup | PASS | CI #459 on `056bf7473ff851157f4c749f233fb0fb8b57a133`: Linux full release checks PASS and Windows PowerShell 5.1 PASS. |

## Deferred / non-blocking observations

| ID | Scenario | Status | Boundary |
|---|---|---|---|
| CERT-NATURAL | Natural renewal-driven Windows rotation | PENDING / DEFERRED | Observe next real renewal; do not force production issuance solely for evidence. |
| RL-006 | Final exact-Windows one-process observation | PARTIAL PASS | Optional original-fixture observation only; do not repeat prior reconnect stress. |
| SEC-004 | Revoked-credential fixture | FIXTURE-UNAVAILABLE | Do not reconstruct revoked credentials solely for artificial evidence. |

Never store secrets or unnecessary production identifiers in evidence files.
