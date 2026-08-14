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
| CERT-007 | Renewal scheduler inventory | PASS | Certbot venv install had no existing systemd/cron renewal schedule; gap confirmed before mutation. |
| CERT-008 | Hermes-owned renewal timer/service | PASS | systemd service/timer enabled and active; bounded not-due smoke succeeded; TCP 80 returned free. |
| CERT-009 | Server lifecycle productization | PASS | PR #29 immutable live adoption reused existing production lineage without serial change; helper/timer/config accepted. |
| CERT-010 | Windows listener inventory | PASS | Win10 Pro 19045 x64 + PowerShell 5.1 x64; default self-signed hash type `1`; exact rollback thumbprint known; TermService and TCP 3389 healthy. |
| CERT-011A | Authenticated trusted certificate delivery/import | PASS | Device-authenticated package retrieval; CNG private key non-exportable; `NETWORK SERVICE` Read ACL; CUSTOM listener binding; TCP 3389 remained listening. |
| CERT-011B | External trusted Microsoft RDP behavior | PASS | Fresh Hermes RDP connection reported server authenticity verified; production Let’s Encrypt certificate accepted without prior self-signed warning. |
| CERT-011C | Initial default-self-signed rollback method | FAIL / CONFIRMED BUG | Attempt to assign old default self-signed thumbprint as CUSTOM through CIM returned `HRESULT 0x80041008`. |
| CERT-011D | Default-self-signed rollback root cause/fix | RESOLVED / LIVE-ACCEPTED | Original type `1` had no explicit custom registry binding. Removing the binding restored exact original self-signed thumbprint/type and TCP 3389; external warning returned. |
| CERT-011E | Fixed trusted reapply | PASS | Fixed sync restored CUSTOM trusted thumbprint; fresh external Microsoft RDP was trusted again. |
| CERT-011F | PR #30 merge | PASS | PR #30 merged after complete live acceptance as `a03e406aaafeb5833bc720d3eef62cca60818118`. |
| CERT-012A | Automatic rotation implementation/final CI | PASS | Final PR #31 head `14da128328589dfae6c8e3b6819977120be16739`; CI #353 Linux full release checks PASS + Windows PowerShell 5.1 PASS. |
| CERT-012B | Server non-secret certificate state deploy | PASS | Transactional deploy PASS; cert serial unchanged; state ACL/fields/thumbprint accepted. |
| CERT-012C | Renewal/status server path | PASS | Authenticated status endpoint + renewal smoke PASS; controller/sshd/timer active; TCP 80 free. |
| CERT-012D | Windows worker unchanged-state setup | PASS | `SEC005 TEST` returned `CERT_ROTATION=UNCHANGED`; task Running; LocalSystem SID `S-1-5-18`. |
| CERT-012E | Rotation setup upgrade global mutex ACL | FAIL / CONFIRMED BUG | Existing SYSTEM-owned global mutex caused administrator preflight Access denied; setup rollback PASS. |
| CERT-012F | Rotation setup mutex fix | RESOLVED / LIVE-ACCEPTED | Existing worker stopped before preflight; mutex ACL limited to LocalSystem + Builtin Administrators; CI/live accepted. |
| CERT-012G | Automatic local self-signed drift recovery | PASS | Worker detected controlled drift, invoked sync, logged `CERT_ROTATION=UPDATED`, restored trusted CUSTOM listener, kept TCP 3389 and task Running. |
| CERT-012H | External trust after automatic recovery | PASS | Fresh Microsoft RDP after automatic recovery was trusted with no self-signed warning. |
| CERT-012I | PR #31 merge | PASS | PR #31 merged as `bd25db552aae8303356953fe2807a7bd855cba95`. |
| CERT-012J | Natural renewal-driven rotation | PENDING / DEFERRED | Observe real future renewal; do not force production issuance solely for evidence. |

## CERT-013 normal Windows lifecycle integration

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CERT-013A | Lifecycle implementation + CI | PASS | PR #32 accepted product/test code head `e11cf89ed26d551ca92b4010034d6e6792a9266b`; reconcile CI #381 Linux full release checks PASS + Windows PowerShell 5.1 PASS. Later evidence-only commits do not change CERT-013 product/test files. |
| CERT-013B | Transactional Update integrates certificate companion | PASS | Live `SEC005 TEST`: `CERT_ROTATION=UNCHANGED`, `CERT-012_SETUP=PASS`, `UPDATE=PASS`, `CertificateRotation: managed`, identity/keys/known_hosts/device ID/RDP port unchanged, one Agent + one Hermes SSH process, rotation task Running as SID `S-1-5-18`, CUSTOM listener + TCP 3389 preserved, final `CERT-013_UPDATE=PASS`. |
| CERT-013C | Repair restores missing rotation scaffolding | PASS | Live `SEC005 TEST`: only rotation task + worker removed; public Repair returned `REPAIR=PASS` + `CERT-013_REPAIR=PASS`; identity/port/tunnel/trusted binding unchanged; worker/task recreated as LocalSystem; TCP 3389 preserved; final `CERT-013_REPAIR_LIVE=PASS`. |
| CERT-013D | Clean disposable fixture preflight | PASS | `DESKTOP-T9N368F`: Windows 10 Pro build 19045 x64, PowerShell 5.1 x64, Defender AV + real-time protection True, OpenSSH Client Installed, Hermes base/task/process state absent; final `CERT-013_CLEAN_FIXTURE=PASS`. |
| CERT-013E | Fresh install manages certificate lifecycle automatically | PASS | Exact accepted head `e11cf89e...`; `CERT_ROTATION=UPDATED`, `CERT-012_SETUP=PASS`; device `CERT013 FRESH`, endpoint `150.241.94.110:53394`; main task/one Agent/one Hermes SSH healthy; rotation task LocalSystem SID `S-1-5-18`; CUSTOM trusted thumbprint `2E170C609B47E0D34F16238503998509EDDDC79C`; TCP 3389; Defender remained enabled with no Hermes exclusion; final `CERT-013_FRESH_INSTALL=PASS`. |
| CERT-013F | Fresh-install external trusted RDP | PASS | User connected through `150.241.94.110:53394`; Microsoft RDP worked and certificate was trusted with no warning. |
| CERT-013G | Normal uninstall removes full client runtime | PASS | Disposable fixture: both Hermes tasks absent; Agent/rotation/SSH counts all zero; active `C:\ProgramData\HermesRDP` absent; archive `C:\ProgramData\HermesRDP.removed.20260814-132332` validated; Defender real-time protection remained True; final `CERT-013_UNINSTALL=PASS`. |

## Current exact acceptance boundary

CERT-001 through CERT-012 bounded behavior is complete. CERT-013 Update, Repair, clean Fresh Install, external trusted RDP and Uninstall are fully live proven on PR #32 accepted product/test code head `e11cf89ed26d551ca92b4010034d6e6792a9266b`.

PR #32 has no remaining live product gate. Evidence-only context/release commits after `e11cf89e...` do not invalidate the accepted code boundary. The next repository action is final CI on the evidence head, ready-for-review transition and exact-head merge.

Natural renewal-driven rotation remains a future observation, not a merge blocker.

## Update triggers

Update this ledger after a new bounded live acceptance, confirmed root cause, code+CI gate, deployment provenance change, or explicit acceptance-boundary change. Never convert an untested requirement to PASS merely because code exists.
