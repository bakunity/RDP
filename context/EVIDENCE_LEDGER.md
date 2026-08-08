# Hermes RDP — Evidence Ledger

Updated: 2026-08-08

Purpose: durable project evidence that survives chat compression. This file records demonstrated facts, confirmed failures/root causes, and explicit revalidation obligations. It is not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source contradiction or explicit user confirmation exists.
- **BASELINE PASS** — PASS is real for the tested build/scenario, but relevant later code changed and the new build must not inherit the result automatically.
- **REVALIDATION REQUIRED** — a prior PASS exists, but current changes touch the behavior enough that the current build needs a smoke/acceptance test.
- **IMPLEMENTED, NOT VALIDATED** — code exists and may have CI coverage, but the real runtime scenario has not yet been accepted.
- **FAIL / CONFIRMED BUG** — failure was reproduced or contradictory source logic was directly established.
- **HYPOTHESIS** — normally belongs in `ACTIVE_WORK.md`; do not promote it here as fact.

## Evidence scope rule

A PASS proves the **scenario/build boundary that was actually tested**. It is not a timeless property inherited by every future commit.

When relevant code changes:

1. preserve the original PASS as historical/baseline evidence;
2. add a `REVALIDATION REQUIRED` row for the changed build;
3. do not downgrade the old evidence to “never worked”;
4. promote the new row to PASS only after current-build runtime evidence.

Critical evidence should be self-contained enough that a future chat can understand the decisive result without the original conversation transcript.

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
| CT-001 | OFF interrupts active RDP access | PASS | User-visible active session/access was interrupted on tested OpenSSH build. |
| CT-002 | ON restores RDP access | PASS | User reconnected after ON on tested build. |
| CT-003 | OFF -> server listener CLOSED | PASS | Linux-side listener measurement on assigned RDP port showed CLOSED on tested stabilization build. |
| CT-004 | ON -> server listener OPEN | PASS | Server-authoritative endpoint state showed OPEN after tunnel returned on tested stabilization build. |
| CT-005 | Agent remains ONLINE while access is OFF | PASS | Live dashboard showed agent heartbeat online with desired/applied OFF and SSH disconnected. |
| CT-006 | Desired state and applied-agent state are independently visible | PASS | Live OFF and ON dashboard states matched expected values. |

## RDP channel classification

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RC-001 | Direct Windows RDP over LAN/VPN is identified as direct | BASELINE PASS | Live Windows socket had non-loopback remote IPv6; Telegram showed Hermes=0, direct=1 before the low-cost query refactor. |
| RC-002 | RDP through Hermes is identified as Hermes | BASELINE PASS | Live Windows socket was loopback `127.0.0.1 -> :3389`; Telegram showed Hermes=1, direct=0 before the low-cost query refactor. |
| RC-003 | Open Hermes endpoint alone does not count as active Hermes RDP session | BASELINE PASS | While connected directly, SSH tunnel/endpoint were open but Hermes RDP counter remained 0 before the low-cost query refactor. |

## Windows compatibility / installer

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| WI-001 | Normal x64 Windows OpenSSH client installation | PASS | Fresh tested installation completed and tunnel worked. |
| WI-002 | Win10 x64 under x86 PowerShell sees native OpenSSH through `Sysnative` | PASS | Real machine: x86 PowerShell, x64 OS, System32 redirected, Sysnative native `ssh.exe`/`ssh-keygen.exe` available; native `ssh.exe -V` ran. |
| WI-003 | Patched fresh full install from x86 PowerShell | IMPLEMENTED, NOT VALIDATED | Resolver exists; final clean end-to-end fresh-install acceptance remains. |
| WI-004 | Existing valid installation protected from duplicate `Добавить ПК` destructive actions | PASS | Live tested: task remained Running, one Hermes SSH process remained, identity/port preserved. |
| WI-005 | Old duplicate-add behavior could stop working task before pair failure | CONFIRMED BUG / RESOLVED ON TESTED BUILD | Reproduced before guard; task/process had to be restored. Guard later live-accepted in WI-004. |
| WI-006 | Windows Server was incorrectly rejected by installer ProductType gate | CONFIRMED BUG | Source blocked `ProductType != 1` while later Caption regex included Server; user reproduced rejection on Windows Server. |
| WI-007 | Windows Server support after ProductType fix | IMPLEMENTED, NOT VALIDATED | ProductType 2/3 support + regression test exist; real fresh install still required. |

## Agent / telemetry performance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PF-001 | Full Established TCP scan is expensive on MIPC | CONFIRMED | Measured ~1059 ms. |
| PF-002 | RDP-only TCP query is cheaper but still non-trivial | CONFIRMED | Measured ~516 ms. |
| PF-003 | Full `Win32_Process` scan is expensive | CONFIRMED | Measured ~357 ms. |
| PF-004 | TOP-process sample has at least an 800 ms sampling window | CONFIRMED | Agent implementation/measurement boundary. |
| PF-005 | Old 3-second telemetry loop could consume most of its own interval | CONFIRMED REGRESSION | Combined measured heavy operations align with observed RDP micro-freezes. |
| PF-006 | Split fast/background/on-demand telemetry materially removes the regression | IMPLEMENTED, NOT VALIDATED | Code/CI complete; new timing + subjective RDP acceptance required. |
| PF-007 | Background resources ~15s, observe resources ~3s/TOP ~6s | IMPLEMENTED, NOT VALIDATED | Runtime cadence still needs observation. |
| PF-008 | `НАБЛЮДАТЬ 60с` automatically stops heavy telemetry/live render | IMPLEMENTED, NOT VALIDATED | Server/agent logic exists; live 60-second lease acceptance required. |

## Server / branch acceptance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| SV-001 | Server updater creates backup and keeps both Hermes services active | PASS | Multiple updater runs returned both services active and backup paths. |
| SV-002 | Server-side endpoint listener truth replaces client self-probe | PASS | Live OFF false-positive was eliminated; dashboard matched Linux listener CLOSED/OPEN. |
| SV-003 | Latest performance/observation/Windows-Server branch head is deployed | NOT YET | Newest changes are CI-passed but not yet live-deployed at this checkpoint. |

## Current-head revalidation obligations

These rows exist because the newest agent changes touched code paths that previously had PASS evidence. They are **not failures**; they prevent old evidence from being over-applied to a new build.

| ID | Scenario on current low-cost telemetry build | Status | Why revalidate |
|---|---|---|---|
| RV-001 | Direct LAN/VPN RDP still reports Hermes=0, direct=1 | REVALIDATION REQUIRED | `Get-RdpConnectionSummary` changed from full Established table to limited RDP/exact-peer queries. |
| RV-002 | Hermes public RDP still reports Hermes=1, direct=0 | REVALIDATION REQUIRED | Same classifier refactor affects loopback peer correlation. |
| RV-003 | Open endpoint without Hermes RDP client still reports Hermes=0 | REVALIDATION REQUIRED | Confirms the optimized classifier still avoids false session counts. |
| RV-004 | Telegram OFF/ON command delivery and tunnel transition still work | REVALIDATION REQUIRED | Agent main polling/telemetry loop was materially restructured; baseline CT-001/002 remain valid for the older tested build. |
| RV-005 | Exactly one Hermes `ssh.exe` remains in normal ON state | REVALIDATION REQUIRED | SSH process lookup/filter/reuse changed during optimization. |
| RV-006 | Endpoint truth remains CLOSED/OFF and OPEN/ON after current-head smoke test | REVALIDATION REQUIRED | Server listener helper itself is baseline-PASS, but current full control path should be smoke-tested after latest deploy. |

## Current branch CI evidence

- PR #19: `fix/control-state-dashboard`.
- Current PR head at checkpoint: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- CI #110: PASS on that branch state.
- Earlier code head `f4d824bf1853d2cd1a9c2a42fecf3374456b3cfb` passed Linux full release checks, PowerShell 5.1 parse and certificate pinning in CI #109.

CI is evidence of source/static correctness only. It does **not** promote Windows Server install, telemetry performance, 60-second observation or current-build revalidation rows to PASS.

## Update triggers

Update this ledger immediately when:

1. live acceptance becomes PASS or FAIL;
2. suspected bug becomes confirmed root cause;
3. confirmed bug is fixed and separately live-accepted;
4. a code change can invalidate an older PASS — preserve baseline + add revalidation row;
5. an evidence boundary becomes clearer;
6. a release boundary triggers ledger snapshot/compaction.

Do not add routine commands, intermediate debug output or speculative ideas.