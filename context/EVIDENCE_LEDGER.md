# Hermes RDP — Evidence Ledger

Updated: 2026-08-10

Purpose: durable project evidence that survives chat compression. This file records demonstrated facts, confirmed failures/root causes, and explicit revalidation obligations. It is not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source contradiction or explicit user confirmation exists.
- **BASELINE PASS** — PASS is real for the tested build/scenario, but relevant later code changed and the new build must not inherit the result automatically.
- **REVALIDATION REQUIRED** — a prior PASS exists, but current changes touch the behavior enough that the current build needs a smoke/acceptance test.
- **IMPLEMENTED, NOT VALIDATED** — code exists and may have CI coverage, but the real runtime scenario has not yet been accepted.
- **PARTIAL PASS** — a required subset is live-proven, but the full acceptance condition is not yet complete.
- **FAIL / CONFIRMED BUG** — failure was reproduced or contradictory source logic was directly established.

A PASS proves the tested scenario/build boundary only. Relevant later code changes create a new revalidation obligation rather than rewriting historical evidence.

## Transport / installation baseline

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| TR-001 | OpenSSH reverse RDP architecture works end-to-end | PASS | Real Windows client paired and standard RDP reached it through Hermes. |
| TR-002 | External-network RDP | PASS | RDP connected from a phone over mobile data. |
| TR-003 | Windows reboot recovery | PASS | Tested Windows reboot; agent/tunnel recovered and RDP became usable again. |
| TR-004 | FRP not required in current runtime | PASS | OpenSSH release/runtime validated; FRP removed from active architecture. |

## Telegram control / endpoint truth

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| CT-001 | OFF interrupts active RDP access | PASS | User-visible active session/access interrupted on tested OpenSSH build. |
| CT-002 | ON restores RDP access | PASS | User reconnected after ON on tested build. |
| CT-003 | OFF -> server listener CLOSED | PASS | Linux-side listener on assigned endpoint showed CLOSED. |
| CT-004 | ON -> server listener OPEN | PASS | Server-authoritative listener state showed OPEN after tunnel returned. |
| CT-005 | Agent remains online while access is OFF | PASS | Live dashboard showed heartbeat online with desired/applied OFF and SSH disconnected. |
| CT-006 | Desired and applied access are independently visible | PASS | Live OFF and ON dashboard states matched expected values. |

## RDP channel classification

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RC-001 | Direct Windows RDP over LAN/VPN is identified as direct | PASS | Revalidated on current head `c51ed8fa...`: live direct session reported `Hermes=0/direct=1` while Hermes tunnel remained enabled. |
| RC-002 | RDP through Hermes is identified as Hermes | PASS | Revalidated on current head `c51ed8fa...`: live Hermes session reported `Hermes=1/direct=0`, proving current loopback peer correlation in a real session. |
| RC-003 | Open Hermes endpoint alone does not count as active Hermes RDP | PASS | Revalidated on current head `c51ed8fa...`: tunnel/endpoint open with no RDP client reported `Hermes=0/direct=0`. |

## Windows compatibility / installer

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| WI-001 | Normal x64 Windows OpenSSH installation | PASS | Fresh tested installation completed and tunnel worked. |
| WI-002 | Win10 x64 under x86 PowerShell reaches native OpenSSH via `Sysnative` | PASS | Real Win10 Pro build 19045 showed x64 OS + 32-bit `SysWOW64` PowerShell, `Sysnative` visibility for native `ssh.exe`/`ssh-keygen.exe`, and successful native OpenSSH execution. |
| WI-003 | Patched fresh full install from x86 PowerShell | PARTIAL PASS | Real Win10 Pro 19045 x64 target ran elevated 32-bit PowerShell under `SysWOW64`; previous local Hermes install was archived intact so active Hermes dir/task were absent; immutable current-head installer `c51ed8...` then completed to `=== ГОТОВО ===`, created a new device registration, assigned endpoint and Scheduled Task, and reported OpenSSH transport. Remaining: post-install canonical System32 SSH path/key/task/one-SSH/current-agent checks plus real RDP endpoint connection. |
| WI-004 | Existing valid installation protected from duplicate Add destructive actions | PASS | Task remained Running, one Hermes SSH process remained, identity/port preserved. |
| WI-005 | Old duplicate-add behavior could stop working task before pair failure | CONFIRMED BUG / RESOLVED ON TESTED BUILD | Reproduced before guard; later guard live-accepted. |
| WI-006 | Windows Server incorrectly rejected by installer ProductType gate | CONFIRMED BUG | Real Windows Server reproduced the old client-only rejection; source logic confirmed contradiction. |
| WI-007 | Windows Server ProductType fix allows real fresh install | PASS | Clean Windows Server 2019 Datacenter, ProductType=3, x64, PowerShell 5.1, no Hermes dir/task. Fresh immutable install reached `=== ГОТОВО ===`, created OpenSSH tunnel/task and assigned endpoint; old client-only rejection did not occur. Installer code matched current PR implementation. |
| WI-008 | Windows Server newest `c51ed8...` agent stack works end-to-end | PASS | Agent-only update to immutable `c51ed8...` preserved device ID, RDP port, config and private key; Task=`Running`; exactly one Hermes `ssh.exe`; expected fast-path markers present; real RDP connection through the assigned Hermes endpoint succeeded after the update. |

## Agent / telemetry performance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PF-001 | Full Established TCP scan is expensive on MIPC | CONFIRMED | Measured ~1059 ms. |
| PF-002 | RDP-only NetTCPIP query is expensive on MIPC | CONFIRMED | First measurement ~516 ms; later 5-run average on deployed low-cost head ~829 ms with max ~1347 ms. |
| PF-003 | Full `Win32_Process` scan is expensive | CONFIRMED | Measured ~357 ms; filtered `Name='ssh.exe'` on first low-cost head still averaged ~256 ms. |
| PF-004 | TOP-process sample has an 800 ms sampling window | CONFIRMED | Agent implementation. |
| PF-005 | Old 3-second telemetry loop could consume most of its interval | CONFIRMED REGRESSION | Measured heavy operations aligned with observed RDP micro-freezes. |
| PF-006 | First split fast/background/on-demand telemetry fully removes regression | FAIL / INCOMPLETE FIX | Heavy CPU/RAM/process work moved off 3s path, but RDP NetTCPIP + SSH WMI remained too expensive. |
| PF-007 | Background resources ~15s, observe resources ~3s/TOP ~6s | PASS | Current-head observation card showed resource age ~3s and populated TOP snapshot age 7s while countdown was active; ordinary background behavior remained healthy before/after observation. |
| PF-008 | `НАБЛЮДАТЬ 60с` automatically stops heavy telemetry/live render | PASS | Live current-head sequence proved countdown/live resource+TOP cadence, then automatic return to `Наблюдение выключено` after lease expiry without manual stop. |
| PF-009 | Second fast-path optimization removes NetTCPIP/WMI bottleneck from ordinary 3s loop | PASS | Live on MIPC head `c51ed8fa...`: cached SSH PID avg 21.63 ms, .NET RDP snapshot avg 19.68 ms, combined FAST core avg 27.46 ms / max 43.69 ms. Full SSH WMI refresh remained ~312.72 ms avg but is no longer ordinary per-cycle work. |
| PF-010 | Overall subjective RDP performance after second optimization | PASS | On the accepted working Hermes path, user reported normal work is comfortable, smooth and free of noticeable micro-freezes; clearly better than before. No noticeable ~15-second periodic stall was reported. |

## Network / latency evidence

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| NW-001 | External client PC -> public Hermes RTT | CONFIRMED | 30 ICMP samples: 0% loss, min 86 ms, avg 101 ms, max 129 ms. |
| NW-002 | MIPC ping/TCP-connect while Karing owns the route directly measures physical VPS latency | INVALIDATED | Local TUN interception made the 0–3 ms / low-ms values local proxy acceptance, not remote RTT. |
| NW-003 | New SSH connection / remote banner timing through Karing | CONFIRMED WITH SCOPE | 10 samples: min 783.2 ms, avg 804.7 ms, max 870.9 ms; includes proxy/TCP setup + SSH banner wait, not RTT. |
| NW-004 | End-to-end RDP negotiation through established Hermes tunnel | CONFIRMED | TCP connect median ~92 ms with one 1092.7 ms outlier; RDP response min 302.7 ms, median 332.4 ms, avg 350.1 ms, max 471.2 ms. |
| NW-005 | Temporary Hermes-only direct-route bypass actually bypasses Karing | PASS | Physical Wi-Fi route selected; real Hermes ICMP 85–95 ms, avg 89 ms, TTL 52. |
| NW-006 | Direct Wi-Fi route improves steady-state Hermes RDP | FAIL | After recreating the tunnel on direct Wi-Fi, subjective RDP became materially worse and Windows connection-quality bars dropped. |
| NW-007 | Restored/working Hermes path is usable for normal RDP work | PASS | User reported smooth operation with no noticeable lag/micro-freezes and clear improvement over pre-optimization behavior. |

## Deployment / provenance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| SV-001 | Server updater creates backup and keeps both Hermes services active | PASS | Multiple updater runs returned both services active and backup paths. |
| SV-002 | Linux listener is authoritative endpoint truth | PASS | Earlier Windows false-positive disappeared; dashboard matched Linux CLOSED/OPEN. |
| SV-003 | Immutable head `586e944...` deployed server-side | PASS | Both services active and rollback backup created. |
| SV-004 | MIPC updated to `586e944...` without identity loss | PASS | Task Running; device ID, config hash, private-key hash and assigned port unchanged; exactly one Hermes `ssh.exe`; local backup created. |
| SV-005 | MIPC updated to current agent head `c51ed8fa...` without identity loss | PASS | Task Running; identity/config/key/port unchanged; .NET TCP path, 15-second SSH PID cache and loopback peer helper present; executable `Get-NetTCPConnection` absent; rollback copy created. |
| SV-006 | Windows Server updated in place to current agent head `c51ed8fa...` without identity loss | PASS | Task Running; device ID/port/config/key preserved; one Hermes SSH process; expected current-head fast-path markers present; rollback copy created; subsequent real RDP connection succeeded. |

## Current-head revalidation obligations

| ID | Scenario on newest fast-path head | Status | Evidence / boundary |
|---|---|---|---|
| RV-001 | Direct LAN/VPN RDP -> Hermes=0/direct=1 | PASS | Live current-head direct RDP card showed exactly `0/1`. |
| RV-002 | Hermes RDP -> Hermes=1/direct=0 | PASS | Live current-head Hermes RDP card showed exactly `1/0`. |
| RV-003 | Open endpoint with no Hermes RDP client -> Hermes=0/direct=0 | PASS | Live current-head card showed endpoint/tunnel open and both counters zero. |
| RV-004 | Telegram OFF/ON command delivery and tunnel transition | PASS | Current-head OFF and ON states both applied successfully. |
| RV-005 | Exactly one Hermes `ssh.exe` in normal ON state | PASS | After OFF -> ON, live PowerShell check returned `HermesSshCount=1` and Scheduled Task `Running`. |
| RV-006 | Endpoint CLOSED/OFF and OPEN/ON on newest head | PASS | Current-head dashboard showed CLOSED+SSH disconnected on OFF and OPEN+SSH connected on ON. |

Targeted current-head smoke RV-001..RV-006 is **COMPLETE**. Do not re-run wholesale without a concrete regression reason.

## Pairing behavior

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PA-001 | Pair code TTL is 15 minutes by default | CONFIRMED | Config default is 900 seconds and DB expiry enforces it. |
| PA-002 | Pair code does not auto-rotate every 15 minutes | INTENDED | New code is generated by explicit Add action; expired code is rejected. |

## Current branch CI

- PR #19: `fix/control-state-dashboard`.
- Current head: `c51ed8fa2c090dbc731a0c06f357d899846e90ae`.
- CI #139: PASS, including Linux release checks and Windows PowerShell 5.1 parse/certificate pinning.
- CI does not replace runtime acceptance.

## Remaining acceptance before merge

1. finish Win10 x86 post-install smoke and real endpoint test;
2. reconcile feature branch with current `main`, rerun CI and recheck mergeability;
3. merge only after acceptance is green or remaining scenarios are explicitly split with evidence boundaries.

## Update triggers

Update this ledger when live acceptance becomes PASS/FAIL, a root cause is confirmed, deployment provenance changes, a fix is live-accepted, or relevant code invalidates an older PASS. Do not add routine commands, pairing codes, tokens or speculative ideas.