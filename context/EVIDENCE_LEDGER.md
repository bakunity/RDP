# Hermes RDP — Evidence Ledger

Updated: 2026-08-12

Purpose: durable project evidence that survives chat compression. This file records demonstrated facts, confirmed failures/root causes, and explicit revalidation obligations. It is not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source contradiction or explicit user confirmation exists.
- **PARTIAL PASS** — a required subset is live-proven, but the full acceptance condition is not yet complete.
- **FAIL / CONFIRMED BUG** — failure was reproduced or contradictory source logic was directly established.
- **RESOLVED / LIVE-ACCEPTED** — a confirmed bug has code, CI and bounded real-runtime acceptance proving the intended correction.

A PASS proves the tested scenario/build boundary only. Relevant later code changes create a new revalidation obligation rather than rewriting historical evidence.

## Transport / installation baseline

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| TR-001 | OpenSSH reverse RDP architecture works end-to-end | PASS | Real Windows client paired and standard Microsoft RDP reached it through Hermes. |
| TR-002 | External-network RDP | PASS | RDP connected from a phone over mobile data. |
| TR-003 | Windows reboot recovery | PASS | Tested Windows reboot; agent/tunnel recovered and RDP became usable again. |
| TR-004 | FRP not required in current runtime | PASS | OpenSSH release/runtime validated; FRP removed from active architecture. |

## Telegram control / endpoint truth

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CT-001 | OFF interrupts active RDP access | PASS | Active Hermes RDP session was interrupted when access was turned OFF. |
| CT-002 | ON restores RDP access | PASS | User reconnected successfully after ON. |
| CT-003 | OFF -> server listener CLOSED | PASS | Linux-side listener on assigned endpoint showed CLOSED. |
| CT-004 | ON -> server listener OPEN | PASS | Server-authoritative listener state showed OPEN after tunnel returned. |
| CT-005 | Agent remains online while access is OFF | PASS | Live dashboard showed heartbeat online with desired/applied OFF and SSH disconnected. |
| CT-006 | Desired and applied access are independently visible | PASS | Live OFF/ON dashboard states matched server goal and agent-applied state. |
| UI-001 | Dashboard updates command/tunnel state without manual Refresh | RESOLVED / LIVE-ACCEPTED | After final PR #20 server deploy, user confirmed OFF/ON state and buttons update automatically; no `🔄 ОБНОВИТЬ` needed. |
| UI-002 | OFF / RESTART mobile buttons are not truncated | RESOLVED / LIVE-ACCEPTED | Final bot renders OFF and RESTART as separate full-width rows; user confirmed mobile Telegram layout works. |

## RDP channel classification

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RC-001 | Direct LAN/VPN RDP classified as direct | PASS | Current accepted fast-path agent reported `Hermes=0/direct=1`. |
| RC-002 | RDP through Hermes classified as Hermes | PASS | Current accepted fast-path agent reported `Hermes=1/direct=0`. |
| RC-003 | Open endpoint alone does not count as active Hermes RDP | PASS | Tunnel/endpoint open with no RDP client reported `Hermes=0/direct=0`. |

## Windows compatibility / installer

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| WI-001 | Normal x64 Windows OpenSSH installation | PASS | Fresh tested installation completed and tunnel worked. |
| WI-002 | Win10 x64 under x86 PowerShell reaches native OpenSSH via Sysnative | PASS | Real Win10 Pro build 19045 showed x64 OS + 32-bit SysWOW64 PowerShell; native `ssh.exe`/`ssh-keygen.exe` resolved through Sysnative and worked. |
| WI-003 | Patched fresh install from x86 PowerShell | PASS | Real Win10 x64 target running 32-bit PowerShell completed immutable install, preserved native OpenSSH paths, created task/key/known_hosts, exactly one Hermes `ssh.exe`, and real RDP succeeded. |
| WI-004 | Existing valid install protected from duplicate Add destructive actions | PASS | Task remained Running; one Hermes SSH process; identity/port preserved. |
| WI-005 | Old duplicate-add path could stop a working task before pair failure | CONFIRMED BUG / RESOLVED | Reproduced before guard; guard later live-accepted. |
| WI-006 | Old Windows Server ProductType gate rejected supported server | CONFIRMED BUG / RESOLVED | Real Windows Server reproduced old rejection; current installer accepts it. |
| WI-007 | Windows Server 2019 fresh install | PASS | Clean Windows Server 2019 Datacenter completed fresh install, task/tunnel came up, endpoint assigned, old client-only rejection absent. |
| WI-008 | Windows Server current accepted agent stack end-to-end | PASS | Agent update preserved device ID/port/config/private key, task Running, exactly one Hermes SSH process, real RDP succeeded. |

Win10 x64 + PowerShell x86 / WOW64 / Sysnative acceptance is **COMPLETE**. Do not repeat without a concrete regression reason.

## Agent / telemetry performance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PF-001 | Old 3-second telemetry loop could consume most of interval | CONFIRMED REGRESSION | Heavy NetTCPIP/WMI/process operations aligned with observed RDP micro-freezes. |
| PF-002 | Background resources ~15s, observe resources ~3s / TOP ~6s | PASS | Live observation card showed expected resource/TOP cadence and automatic return to background mode. |
| PF-003 | Ordinary fast path removes NetTCPIP/WMI bottleneck | PASS | MIPC accepted agent: cached SSH PID avg ~21.63 ms, .NET RDP snapshot avg ~19.68 ms, combined FAST core avg ~27.46 ms / max ~43.69 ms. |
| PF-004 | Overall subjective RDP performance after optimization | PASS | User reported normal Hermes RDP work is smooth and free of noticeable micro-freezes. |

## Network / latency evidence

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| NW-001 | External client PC -> public Hermes RTT | CONFIRMED | 30 ICMP samples: 0% loss, min 86 ms, avg 101 ms, max 129 ms. |
| NW-002 | Karing-routed local low-ms probes measure physical VPS RTT | INVALIDATED | Local TUN interception made the values local proxy acceptance, not remote RTT. |
| NW-003 | End-to-end RDP negotiation through established Hermes tunnel | CONFIRMED | TCP connect median ~92 ms; RDP response median ~332 ms on measured path. |
| NW-004 | Temporary direct Wi-Fi route improves steady-state Hermes RDP | FAIL | User reported materially worse RDP and lower connection-quality bars after direct-route tunnel recreation. |
| NW-005 | Restored working Hermes path is usable for normal work | PASS | User reported smooth operation after optimization/restoration. |

## Deployment / provenance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| SV-001 | Server updater creates rollback backup and keeps services active | PASS | Multiple immutable updater runs returned both Hermes services active and backup paths. |
| SV-002 | Linux listener is authoritative public endpoint truth | PASS | Dashboard CLOSED/OPEN matches server listener; prior Windows-side false-positive removed. |
| SV-003 | Immutable server head `586e944...` deployed | PASS | Both services active and rollback backup created. |
| SV-004 | MIPC updated to `586e944...` without identity loss | PASS | Task Running; device ID/config/private-key/port preserved; one Hermes `ssh.exe`. |
| SV-005 | MIPC updated to fast-path head `c51ed8fa...` without identity loss | PASS | Identity/config/key/port preserved; expected fast-path markers present; one Hermes SSH process. |
| SV-006 | Windows Server updated to `c51ed8fa...` without identity loss | PASS | Identity/config/key/port preserved; one Hermes SSH process; subsequent real RDP succeeded. |
| SV-007 | PR #20 head `2a170b0f...` server deploy | PASS | Immutable updater returned both services active and backup `/var/backups/hermes-rdp/update-20260812T082204Z`. |
| SV-008 | MIPC agent updated to PR #20 control-first agent `2a170b0f...` | PASS | Task Running; DeviceId/port/config/key unchanged; one Hermes SSH process; control-first/desired-sync/transport-split markers present. |
| SV-009 | Final PR #20 server/controller head `77240e2d...` deployed without restarting sshd | PASS | Controller changed and stayed active; `/healthz` OK; configured repository ref exact; dedicated sshd PID stayed unchanged; rollback `/var/backups/hermes-rdp/controller-20260812T095505Z`. |

## Current-head smoke retained

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RV-001 | Direct LAN/VPN RDP -> Hermes=0/direct=1 | PASS | Live card showed exactly `0/1`. |
| RV-002 | Hermes RDP -> Hermes=1/direct=0 | PASS | Live card showed exactly `1/0`. |
| RV-003 | Open endpoint/no Hermes RDP -> Hermes=0/direct=0 | PASS | Live card showed endpoint open and both counters zero. |
| RV-004 | Telegram OFF/ON command delivery and tunnel transition | PASS | OFF and ON applied successfully. |
| RV-005 | Exactly one Hermes `ssh.exe` in normal ON state | PASS | Live PowerShell check returned one Hermes SSH process and task Running. |
| RV-006 | Endpoint CLOSED/OFF and OPEN/ON | PASS | Dashboard/server truth matched both transitions. |

Targeted RV-001..RV-006 is **COMPLETE**. Do not re-run wholesale without a concrete regression reason.

## Pairing behavior

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PA-001 | Pair code TTL is 15 minutes by default | CONFIRMED | Config default is 900 seconds and DB expiry enforces it. |
| PA-002 | Pair code does not auto-rotate every 15 minutes | INTENDED | Explicit Add action generates a new code; expired code is rejected. |

## PR #19 repository acceptance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PR19-001 | Reconcile feature branch with advanced main | PASS | Reconciliation merge had feature/main parents; branch became behind=0 while intended product diff stayed intact. |
| PR19-002 | Reconciled CI | PASS | CI #175: Linux PASS and Windows PowerShell 5.1 PASS. |
| PR19-003 | PR #19 merged | PASS | Merge commit `3f81bde44208df40e1a2753dcadb8397211b9255` became main. |

PR #19 scope is **COMPLETE**.

## PR #20 soak-stabilization acceptance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PR20-001 | Initial stabilization implementation CI | PASS | Head `2a170b0f...`; CI #207 Windows PowerShell 5.1 PASS and Linux full release checks PASS. |
| PR20-002 | CP-001 bounded live acceptance | PASS | Silent raw TCP connection held `:7443` for 15s while five parallel `/healthz` calls all passed in 16–20 ms; controller/sshd PIDs unchanged; active telemetry stayed fresh. |
| PR20-003 | CU-001 existing OSIO stale command acceptance | PASS | Seq 14 OFF timed out: desired OFF remained durable, pending cleared, timeout result retained seq/action, endpoint stayed CLOSED. |
| PR20-004 | CL-001 direct desired-state acceptance | PASS | On MIPC, server desired OFF was changed without queueing a command; seq stayed 27. Agent remained online, applied OFF/SSH=0/listener closed within 5s, then restored desired ON/one SSH/listener open within 8s, still same seq. |
| PR20-005 | Late command-result after timeout guard | PASS | Registry now rejects completion when no pending command remains or action/seq do not match; regression tests cover timeout then late same-seq result and old result after a newer command. |
| PR20-006 | Final UI/server follow-up CI | PASS | Head `77240e2d...`; CI #210 Windows PowerShell 5.1 PASS and Linux full release checks PASS. |
| PR20-007 | Final controller-only live deploy | PASS | Controller active and health OK on exact head; dedicated sshd PID unchanged. |
| PR20-008 | Telegram UI auto-refresh/mobile layout | PASS | User confirmed automatic post-command updates and full-width OFF/RESTART rows on mobile. |
| PR20-009 | PR #20 merged to main | PASS | GitHub merged expected head `77240e2d...`; merge commit `dcda9d3890be390a90e9a967905f2cab3c6c7194`. |

PR #20 scope is **COMPLETE**. CP-001/CL-001/CU-001 are release-blocker closures, not pending work.

## Recovery / lifecycle acceptance — ACTIVE

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RL-001 | Telegram RESTART replaces Hermes SSH transport and returns one tunnel | PASS | Old SSH PID disappeared, different PID appeared, count returned to 1, access stayed ON; open RDP session recovered automatically. |
| RL-002 | Temporary Windows-side transport/network loss auto-recovers | PASS | Scoped fault killed old Hermes SSH; after removal a different SSH PID returned, count=1, task Running, same command seq; RDP usable again. |
| RL-003 | Linux server reboot recovers services and clients | PASS | Real reboot; server returned, Telegram/dashboard worked, already-open Hermes RDP session restored and was usable. |
| RL-004 | Controller restart isolated from RDP transport | PASS | Controller PID changed; dedicated sshd and endpoint session/listeners stayed; user observed no RDP interruption. |
| RL-005 | Dedicated Hermes sshd restart recovery | PASS | Controller unchanged; sshd/session replaced; listeners returned; RDP recovered automatically and dashboard stayed healthy. |
| RL-006 | Repeated reconnects produce no duplicate/orphan Hermes SSH | PARTIAL PASS | Five dedicated-sshd cycles were clean server-side: old session gone, new session appeared, exactly one endpoint listener and one `:7000`, controller unchanged. Final Windows process count on original machine not collected. Do not repeat five-cycle stress; one later process-count check is enough if machine is available. |
| RL-007 | Two+ devices simultaneously healthy | PARTIAL PASS | Four independent endpoints were simultaneously listening and all four TCP-through-tunnel checks passed. Remaining acceptance is user-facing simultaneous dual-RDP smoke on two devices. |
| RL-008 | One device failure isolated from another | PENDING | Not yet run. Soak blockers no longer pause it; run after RL-007 with smallest reversible one-device fault. |

Windows reboot recovery remains historical PASS (`TR-003`) and is not duplicated as a new Stage 2 obligation.

## Soak-test blockers — historical failures, now resolved

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CP-001 | One stalled TLS connection blocks global HTTPS API acceptance | RESOLVED / LIVE-ACCEPTED | Pre-fix: service active/listener present but local health timed out; backlog saturated; API thread blocked in socket receive; telemetry stopped globally while SSH endpoints stayed alive. Fix moved TLS handshake into per-connection worker with timeout. Bounded live acceptance passed five parallel health requests while a silent raw TCP client remained connected. |
| CL-001 | Desired OFF + local ON deadlocks heartbeat/control delivery | RESOLVED / LIVE-ACCEPTED | Pre-fix OSIO: desired OFF, old local ON, SSH auth rejected, transport-first loop prevented telemetry and pending OFF delivery. Fix makes control poll independent and returns durable desired state. Direct MIPC test with unchanged command seq converged OFF then restored ON automatically. |
| CU-001 | Pending command shown as executing indefinitely | RESOLVED / LIVE-ACCEPTED | Pre-fix OSIO OFF seq stayed pending for hours. Fix adds deterministic timeout preserving desired state and rejects late stale results. Existing live OSIO command timed out correctly with endpoint still closed. |

## Update triggers

Update this ledger when live acceptance becomes PASS/FAIL, a root cause is confirmed, deployment provenance changes, a fix is live-accepted, repository gate state changes, or relevant code invalidates an older PASS. Do not add routine commands, pairing codes, API tokens, private keys, raw external scanner IPs, or speculative ideas.
