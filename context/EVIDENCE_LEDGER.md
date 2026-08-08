# Hermes RDP — Evidence Ledger

Updated: 2026-08-08

Purpose: durable project evidence that survives chat compression. This file records **facts that have actually been demonstrated**, plus confirmed failures/bugs. It is not a TODO list and not a transcript.

## Evidence levels

- **PASS / CONFIRMED** — actual runtime output, CI result, source inspection proving a contradiction, or explicit user confirmation exists.
- **IMPLEMENTED, NOT VALIDATED** — code exists and may have CI coverage, but the real runtime scenario has not yet been accepted.
- **FAIL / CONFIRMED BUG** — the failure was reproduced or the contradictory source logic was directly established.
- **HYPOTHESIS** — do not put here unless needed to explain an unresolved evidence boundary; hypotheses belong primarily in `ACTIVE_WORK.md` / audit notes.

When behavior changes in a way that could invalidate an old PASS, do not delete history silently. Mark the old evidence as baseline and add a new acceptance row for the changed build.

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
| CT-001 | OFF interrupts active RDP access | PASS | User-visible active session/access was interrupted. |
| CT-002 | ON restores RDP access | PASS | User reconnected after ON. |
| CT-003 | OFF -> server listener CLOSED on tested current branch build | PASS | Linux-side listener measurement on assigned RDP port showed CLOSED. |
| CT-004 | ON -> server listener OPEN on tested current branch build | PASS | Server-authoritative endpoint state showed OPEN after tunnel returned. |
| CT-005 | Agent remains ONLINE while access is OFF | PASS | Live dashboard showed agent heartbeat online with desired/applied OFF and SSH disconnected. |
| CT-006 | Desired state and applied-agent state are independently visible | PASS | Live OFF and ON dashboard states matched expected values. |

## RDP channel classification

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| RC-001 | Direct Windows RDP over LAN/VPN is identified as direct | PASS | Live Windows socket had non-loopback remote IPv6; Telegram showed Hermes=0, direct=1. |
| RC-002 | RDP through Hermes is identified as Hermes | PASS | Live Windows socket was loopback `127.0.0.1 -> :3389`; Telegram showed Hermes=1, direct=0. |
| RC-003 | Open Hermes endpoint alone does not count as active Hermes RDP session | PASS | While connected directly, SSH tunnel/endpoint were open but Hermes RDP counter remained 0. |

## Windows compatibility / installer

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| WI-001 | Normal x64 Windows OpenSSH client installation | PASS | Fresh tested installation completed and tunnel worked. |
| WI-002 | Win10 x64 under x86 PowerShell sees native OpenSSH through `Sysnative` | PASS | Real machine: x86 PowerShell, x64 OS, System32 redirected, Sysnative native `ssh.exe`/`ssh-keygen.exe` available; native `ssh.exe -V` ran. |
| WI-003 | Patched fresh full install from x86 PowerShell | IMPLEMENTED, NOT VALIDATED | Resolver exists; final clean end-to-end fresh-install acceptance remains. |
| WI-004 | Existing valid installation is protected from duplicate `Добавить ПК` destructive actions | PASS | Live tested: task remained Running, one Hermes SSH process remained, identity/port preserved. |
| WI-005 | Old duplicate-add behavior could stop working task before pair failure | CONFIRMED BUG | Reproduced on Win10 before guard; task/process had to be restored. Fixed by guard and then live-accepted in WI-004. |
| WI-006 | Windows Server was incorrectly rejected by installer ProductType gate | CONFIRMED BUG | Source directly blocked `ProductType != 1` while later Caption regex included Server; user reproduced rejection on Windows Server. |
| WI-007 | Windows Server support after ProductType fix | IMPLEMENTED, NOT VALIDATED | ProductType 2/3 support + regression test exist; real fresh install still required. |

## Agent / telemetry performance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| PF-001 | Full Established TCP scan is expensive on MIPC | CONFIRMED | Measured ~1059 ms. |
| PF-002 | RDP-only TCP query is cheaper but still non-trivial | CONFIRMED | Measured ~516 ms. |
| PF-003 | Full `Win32_Process` scan is expensive | CONFIRMED | Measured ~357 ms. |
| PF-004 | TOP-process sample has at least an 800 ms sampling window | CONFIRMED | Agent implementation + observed design. |
| PF-005 | Old 3-second telemetry loop could consume most of its own interval | CONFIRMED REGRESSION | Combined measured heavy operations align with observed RDP micro-freezes. |
| PF-006 | Split fast/background/on-demand telemetry removes the regression | IMPLEMENTED, NOT VALIDATED | Code/CI complete; live timing + subjective RDP acceptance still required. |

## Server / branch acceptance

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| SV-001 | Server updater creates backup and keeps both Hermes services active | PASS | Multiple updater runs returned both services active and backup paths. |
| SV-002 | Server-side endpoint listener truth replaces client self-probe | PASS | Live OFF false-positive was eliminated; dashboard matched Linux listener CLOSED/OPEN. |
| SV-003 | Latest performance/observation/Windows-Server branch head is deployed | NOT YET | At this checkpoint newest changes remain CI-passed but not live-deployed. |

## Current branch CI evidence

- PR #19: `fix/control-state-dashboard`.
- Current PR head at checkpoint: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- CI #110: PASS on the current branch state.
- Earlier code head `f4d824bf1853d2cd1a9c2a42fecf3374456b3cfb` passed Linux full release checks, PowerShell 5.1 parse and certificate pinning in CI #109.

CI is evidence of code/static correctness only. It does **not** promote runtime scenarios such as Windows Server fresh install or telemetry performance to PASS.

## Update triggers

Update this ledger immediately when:

1. a live acceptance scenario becomes PASS or FAIL;
2. a suspected bug becomes a confirmed root cause;
3. a previously confirmed bug is fixed and then separately live-accepted;
4. a new code change can invalidate an older PASS and needs a fresh acceptance row;
5. an evidence boundary becomes clearer (for example user-visible PASS vs listener-level PASS).

Do not add routine commands, intermediate debugging output or speculative ideas.