# Hermes RDP — Evidence Ledger

Updated: 2026-08-14

Purpose: durable project evidence that survives chat compression. This file records demonstrated facts, confirmed failures/root causes, and explicit revalidation obligations. It is not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source contradiction or explicit user confirmation exists.
- **PARTIAL PASS** — a required subset is live-proven, but the full acceptance condition is not yet complete.
- **FAIL / CONFIRMED BUG** — failure was reproduced or contradictory source logic was directly established.
- **RESOLVED / LIVE-ACCEPTED** — a confirmed bug has code, CI and bounded real-runtime acceptance proving the intended correction.

A PASS proves the tested scenario/build boundary only. Relevant later code changes create a new revalidation obligation rather than rewriting historical evidence.

## Stable acceptance baseline

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| TR-001 | OpenSSH reverse RDP architecture works end-to-end | PASS | Real Windows clients paired and standard Microsoft RDP reached them through Hermes. |
| TR-002 | External-network RDP | PASS | Real external client connected through the public Hermes endpoint. |
| TR-003 | Windows reboot recovery | PASS | Tested Windows reboot; agent/tunnel recovered and RDP became usable again. |
| TR-004 | Linux reboot recovery | PASS | Real Linux reboot; Hermes services/tunnels recovered and existing RDP access returned. |
| TR-005 | Multi-device simultaneous operation | PASS | Multiple independent endpoints/listeners worked concurrently; simultaneous user-facing RDP sessions were accepted. |
| TR-006 | One-device failure isolation | PASS | Scoped OFF/failure on one device did not disrupt another active Hermes RDP session. |
| CT-001 | Telegram OFF/ON/RESTART control | PASS | OFF interrupted access, ON restored it, RESTART replaced transport and recovered one tunnel. |
| UI-001 | Dashboard automatic state refresh / mobile action layout | RESOLVED / LIVE-ACCEPTED | Accepted after PR #20. |
| WI-001 | Win10 x64 + x86 PowerShell / Sysnative OpenSSH | PASS | Real Win10 Pro build 19045 under SysWOW64 PowerShell completed native OpenSSH install/runtime path. Do not repeat without regression. |
| WI-002 | Windows Server 2019 | PASS | Fresh install/update preserved identity and real RDP worked. |
| PF-001 | Fast-path telemetry avoids prior RDP micro-freeze regression | PASS | Accepted optimized agent reduced ordinary fast core to tens of milliseconds; user reported smooth RDP. |
| UPD-001 | Transactional Linux updater success/rollback | PASS | Immutable server updates create backups and restore on bounded failure. |
| UPD-002 | Transactional Windows updater success/rollback | PASS | Live success and forced-failure rollback preserved identity/task/tunnel. |
| REP-001 | Existing-device Repair success/rollback | PASS | Missing runtime scaffolding repair and forced-failure rollback both live accepted. |
| DEF-001 | Defender coexistence | PASS | Accepted runtime does not require weakening Defender. |

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation; do not repeat the five-cycle stress test.

## Soak / control-plane blocker closures

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CP-001 | Stalled TLS client could block API accept loop | RESOLVED / LIVE-ACCEPTED | TLS handshake moved into per-connection worker with timeout; bounded live slow-client acceptance passed. |
| CL-001 | Desired OFF + local ON could deadlock control delivery | RESOLVED / LIVE-ACCEPTED | Control poll separated from transport reconciliation; live desired-state convergence passed. |
| CU-001 | Pending command could remain executing indefinitely | RESOLVED / LIVE-ACCEPTED | Deterministic timeout preserves desired state and rejects late stale result; live acceptance passed. |

## Trusted public-IP certificate lifecycle

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CERT-001 | Certificate host inventory | PASS | Debian 13; Certbot initially absent; HTTP/HTTPS listener inventory established before mutation. |
| CERT-002 | Isolated Certbot installation | PASS | Certbot 5.7.0 installed under `/opt/certbot`; no Windows listener mutation. |
| CERT-003 | Public TCP 80 / HTTP-01 reachability | PASS | Explicit firewall allow plus five independent external HTTP 200 probes with matching server requests. |
| CERT-004 | Let’s Encrypt staging public-IP issuance | PASS | Standalone HTTP-01 + short-lived IP profile succeeded; critical IP SAN and Server Authentication EKU present. |
| CERT-005 | Staging lineage/key/renewal validation | PASS | Certificate/private-key public-key match PASS; full chain inspected; saved standalone renewal dry-run succeeded; TCP 80 free before/after. |
| CERT-006 | Production public-IP issuance | PASS | Production Let’s Encrypt issuance succeeded; critical IP SAN, Server Authentication EKU, RSA key match and local trust-chain validation PASS. |
| CERT-007 | Renewal scheduler inventory | PASS | Certbot venv install had no existing systemd/cron renewal schedule; gap confirmed before productization. |
| CERT-008 | Hermes-owned renewal timer/service | PASS | systemd service/timer enabled and active; bounded not-due smoke succeeded; TCP 80 returned free. |
| CERT-009 | Server lifecycle productization | PASS | PR #29 immutable live adoption reused existing production lineage without serial change; helper/timer/config accepted. |
| CERT-010 | Windows listener inventory | PASS | Win10 Pro 19045 x64 + PowerShell 5.1 x64; default self-signed hash type `1`; exact rollback thumbprint known; TermService and TCP 3389 healthy. |
| CERT-011A | Authenticated trusted certificate delivery/import | PASS | Device-authenticated package retrieval; CNG private key non-exportable; `NETWORK SERVICE` Read ACL; CUSTOM listener binding; TCP 3389 remained listening. |
| CERT-011B | External trusted Microsoft RDP behavior | PASS | Fresh Hermes RDP connection reported server authenticity verified; production Let’s Encrypt certificate accepted without prior self-signed warning. |
| CERT-011C | Initial default-self-signed rollback method | FAIL / CONFIRMED BUG | Attempt to assign old default self-signed thumbprint as CUSTOM through CIM returned `HRESULT 0x80041008`. |
| CERT-011D | Default-self-signed rollback root cause/fix | RESOLVED / LIVE-ACCEPTED | Original type `1` had no explicit custom registry binding. Removing the binding restored exact original self-signed thumbprint/type and TCP 3389; external warning returned. |
| CERT-011E | Fixed trusted reapply | PASS | Fixed sync restored CUSTOM trusted thumbprint; fresh external Microsoft RDP was trusted again. |
| CERT-011F | PR #30 merge | PASS | PR #30 merged after complete live acceptance as `a03e406aaafeb5833bc720d3eef62cca60818118`. |
| CERT-012A | Automatic rotation code/CI | PASS | Draft PR #31 immutable head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`; CI #344 Linux full release checks PASS + Windows PowerShell 5.1 PASS. |
| CERT-012B | Server non-secret certificate state deploy | PASS | Transactional deploy `UPDATE=PASS`; production cert serial unchanged; state helper installed; state file `root:hermes-rdp` mode `0640`; thumbprint matched current cert; payload limited to expected non-secret fields. |
| CERT-012C | Renewal/status server path | PASS | Authenticated certificate-status endpoint installed; renewal service smoke PASS; controller/sshd/timer active; TCP 80 free after smoke. |
| CERT-012D | Windows rotation worker unchanged-state setup | PENDING | Must install SYSTEM worker on `SEC005 TEST` and prove current trusted CUSTOM binding returns `CERT_ROTATION=UNCHANGED` without full PFX sync. |
| CERT-012E | Automatic local-drift recovery | PENDING | After accepted self-signed rollback, worker must restore trusted CUSTOM binding automatically with no manual reapply. |
| CERT-012F | Natural renewal-driven rotation | PENDING / DEFERRED | Observe a real future renewal thumbprint change; do not force unnecessary production issuance solely for testing. |

## Current exact acceptance boundary

CERT-001 through CERT-011 are complete and should not be repeated without a concrete regression reason. CERT-012 server side is accepted on immutable PR #31 head `79cab42d...`.

Immediate next proof: install the separate SYSTEM rotation worker on `SEC005 TEST`. With the currently correct trusted listener it must report `CERT_ROTATION=UNCHANGED`, keep the listener unchanged, and leave the rotation task Running. Then intentionally create only the already-accepted local self-signed drift and let the worker repair it automatically.

## Update triggers

Update this ledger after a new bounded live acceptance, confirmed root cause, code+CI gate, deployment provenance change, or explicit acceptance-boundary change. Never convert an untested requirement to PASS merely because code exists.
