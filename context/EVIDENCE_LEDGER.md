# Hermes RDP — Evidence Ledger

Updated: 2026-08-14

Purpose: compact current evidence index after the v1.3.0 release boundary. Detailed trusted-certificate/CERT-013 evidence is frozen in `context/archive/releases/v1.3.0-evidence.md`; full release history is in `docs/releases/history/v1.3.0-full.md`.

## Evidence levels

- **PASS / CONFIRMED** — runtime, CI, source or explicit user evidence exists.
- **PARTIAL PASS** — required subset is proven but an optional/original-fixture observation remains.
- **FAIL / CONFIRMED BUG** — failure was reproduced/established.
- **RESOLVED / LIVE-ACCEPTED** — confirmed bug has code, CI and bounded runtime acceptance.

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
