# Hermes RDP — Evidence Ledger

Updated: 2026-08-09

Purpose: durable project evidence that survives chat compression. This file records demonstrated facts, confirmed failures/root causes, and explicit revalidation obligations. It is not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source contradiction or explicit user confirmation exists.
- **BASELINE PASS** — PASS is real for the tested build/scenario, but relevant later code changed and the new build must not inherit the result automatically.
- **REVALIDATION REQUIRED** — a prior PASS exists, but current changes touch the behavior enough that the current build needs a smoke/acceptance test.
- **IMPLEMENTED, NOT VALIDATED** — code exists and may have CI coverage, but the real runtime scenario has not yet been accepted.
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
| RC-001 | Direct Windows RDP over LAN/VPN is identified as direct | BASELINE PASS | Pre-optimization live dashboard showed Hermes=0, direct=1. |
| RC-002 | RDP through Hermes is identified as Hermes | BASELINE PASS | Pre-optimization live dashboard showed Hermes=1, direct=0. |
| RC-003 | Open Hermes endpoint alone does not count as active Hermes RDP | BASELINE PASS | Tunnel/endpoint were open while direct RDP was active; Hermes counter stayed 0. |

## Windows compatibility / installer

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| WI-001 | Normal x64 Windows OpenSSH installation | PASS | Fresh tested installation completed and tunnel worked. |
| WI-002 | Win10 x64 under x86 PowerShell reaches native OpenSSH via `Sysnative` | PASS | Real machine proved WOW64 redirection and successful native `ssh.exe -V`. |
| WI-003 | Patched fresh full install from x86 PowerShell | IMPLEMENTED, NOT VALIDATED | Resolver exists; final clean e2e install remains. |
| WI-004 | Existing valid installation protected from duplicate Add destructive actions | PASS | Task remained Running, one Hermes SSH process remained, identity/port preserved. |
| WI-005 | Old duplicate-add behavior could stop working task before pair failure | CONFIRMED BUG / RESOLVED ON TESTED BUILD | Reproduced before guard; later guard live-accepted. |
| WI-006 | Windows Server incorrectly rejected by installer ProductType gate | CONFIRMED BUG | Real Windows Server reproduced the client-only rejection; source logic confirmed contradiction. |
| WI-007 | Windows Server support after ProductType fix | IMPLEMENTED, NOT VALIDATED | ProductType 2/3 support + regression test exist; real fresh install remains. |

## Agent / telemetry performance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PF-001 | Full Established TCP scan is expensive on MIPC | CONFIRMED | Measured ~1059 ms. |
| PF-002 | RDP-only TCP query is cheaper but non-trivial | CONFIRMED | Measured ~516 ms. |
| PF-003 | Full `Win32_Process` scan is expensive | CONFIRMED | Measured ~357 ms. |
| PF-004 | TOP-process sample has an 800 ms sampling window | CONFIRMED | Agent implementation. |
| PF-005 | Old 3-second telemetry loop could consume most of its interval | CONFIRMED REGRESSION | Measured heavy operations aligned with observed RDP micro-freezes. |
| PF-006 | Split fast/background/on-demand telemetry materially removes regression | IMPLEMENTED, NOT VALIDATED | Exact head deployed; timing + subjective RDP acceptance now required. |
| PF-007 | Background resources ~15s, observe resources ~3s/TOP ~6s | IMPLEMENTED, NOT VALIDATED | Runtime cadence still needs observation. |
| PF-008 | `НАБЛЮДАТЬ 60с` automatically stops heavy telemetry/live render | IMPLEMENTED, NOT VALIDATED | Live 60-second lease acceptance required. |

## Deployment / provenance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| SV-001 | Server updater creates backup and keeps both Hermes services active | PASS | Multiple updater runs returned both services active and backup paths. |
| SV-002 | Linux listener is authoritative endpoint truth | PASS | Earlier Windows false-positive disappeared; dashboard matched Linux CLOSED/OPEN. |
| SV-003 | Exact acceptance head deployed server-side | PASS | Immutable SHA `586e9446ea41262f1ed0d9c84ba72838a47d9bc5` used for updater; both services returned active and backup was created. |
| SV-004 | MIPC updated to same immutable head without identity loss | PASS | Task Running; device ID, config hash, private-key hash and assigned port unchanged; exactly one Hermes `ssh.exe`; local backup created. |

## Current-head revalidation obligations

| ID | Scenario on low-cost telemetry head | Status | Why revalidate |
|---|---|---|---|
| RV-001 | Direct LAN/VPN RDP -> Hermes=0/direct=1 | REVALIDATION REQUIRED | RDP classifier query strategy changed. |
| RV-002 | Hermes RDP -> Hermes=1/direct=0 | REVALIDATION REQUIRED | Loopback peer correlation changed. |
| RV-003 | Open endpoint with no Hermes RDP client -> Hermes=0 | REVALIDATION REQUIRED | Confirms no false active-session count. |
| RV-004 | Telegram OFF/ON command delivery and tunnel transition | REVALIDATION REQUIRED | Main polling/telemetry loop was restructured. |
| RV-005 | Exactly one Hermes `ssh.exe` in normal ON state | PARTIAL PASS | Immediately after current-head MIPC update exactly one Hermes SSH process was present; repeat during ON smoke. |
| RV-006 | Endpoint CLOSED/OFF and OPEN/ON on current head | REVALIDATION REQUIRED | Full control path smoke still required after latest deploy. |

## Pairing behavior

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PA-001 | Pair code TTL is 15 minutes by default | CONFIRMED | Config default is 900 seconds and DB expiry enforces it. |
| PA-002 | Pair code does not auto-rotate every 15 minutes | INTENDED | New code is generated by explicit Add action; expired code is rejected. Future UX may show countdown/expired state + explicit new-code button. |

## Current branch CI

- PR #19: `fix/control-state-dashboard`.
- Acceptance head: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- CI #110: PASS on that branch state.
- CI does not replace runtime acceptance.

## Update triggers

Update this ledger when live acceptance becomes PASS/FAIL, a root cause is confirmed, deployment provenance changes, a fix is live-accepted, or relevant code invalidates an older PASS. Do not add routine commands or speculative ideas.