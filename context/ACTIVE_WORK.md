# Hermes RDP — Active Work

Updated: 2026-08-08 23:45 +03:00

Purpose: this is the **first file to read after `context/README.md`**. It is the continuously refreshed operational checkpoint of the project. It must not wait for the end of a chat.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- Current PR head at this checkpoint: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Latest published release: `v1.1.0`.
- Release target in progress: **v1.2.0 — Stabilization**.
- Draft release notes live on the active branch at `docs/releases/v1.2.0-draft.md`.
- Product code is still unmerged; `main` remains the published-product baseline plus context-only checkpoints.

## What is already live-confirmed

- OpenSSH reverse RDP works end-to-end.
- Real external RDP works.
- Windows reboot -> agent/tunnel/RDP recovery works on the tested PC.
- Telegram OFF interrupts active RDP access; ON restores it.
- Server-side endpoint truth correctly distinguishes CLOSED/OPEN using the Linux listener.
- Current state model separates agent heartbeat, desired access, applied state, SSH transport and endpoint.
- MIPC OFF live state: desired OFF + applied OFF + SSH disconnected + endpoint closed — PASS.
- MIPC ON live state: desired ON + applied ON + SSH connected + endpoint open — PASS.
- RDP channel classification is live-confirmed:
  - direct LAN/VPN session -> Hermes=0, direct=1;
  - Hermes public endpoint session -> Hermes=1, direct=0.
- Existing-install guard on the tested Win10 installation preserves task, identity, key and RDP port.
- Win10 x64 launched from x86 PowerShell can reach native Microsoft OpenSSH through `Sysnative`; this runtime behavior is confirmed.

See `EVIDENCE_LEDGER.md` for the durable acceptance matrix.

## Confirmed bugs / regressions found during current acceptance

### Windows agent telemetry performance

Real timing on MIPC before optimization:

```text
full Established TCP query  ~1059 ms
RDP-only TCP query          ~516 ms
full Win32_Process query    ~357 ms
TopProcesses sample         800 ms minimum
```

The previous 3-second telemetry loop could spend most of its interval doing heavy diagnostics and coincided with RDP micro-freezes.

Status: **CONFIRMED REGRESSION; FIX IMPLEMENTED IN PR; NOT YET LIVE VALIDATED**.

### Windows Server installer gate

The installer rejected Windows Server because `ProductType != 1` was blocked before the later Caption check that already mentioned Server.

Status: **CONFIRMED BUG; FIX IMPLEMENTED IN PR; NOT YET LIVE VALIDATED**.

## Implemented on current PR head, not yet live-accepted

- low-cost telemetry model:
  - fast control/heartbeat path every 3 seconds;
  - heavier resource telemetry every 15 seconds in background;
  - TOP processes disabled in background;
  - explicit `НАБЛЮДАТЬ 60с` lease enables short-lived detailed monitoring;
  - observation auto-disables after 60 seconds;
  - full Established TCP table scan removed from the normal RDP classifier;
  - SSH process lookup narrowed/reused inside a cycle;
- Telegram dashboard 3-second auto-render only while an observation lease is active;
- Russian user-facing status vocabulary and controls;
- Windows Server ProductType 2/3 support in the installer.

CI for the latest active branch state is green; runtime acceptance is still required for the items above.

## Deployment truth

- A pre-performance-fix PR build is already deployed on the working server and has passed live OFF/ON + endpoint + RDP-channel acceptance.
- The newest performance/observation/Windows-Server changes have **not yet been live-deployed/accepted** at this checkpoint.
- Do not claim current PR head is production/live merely because CI passes.

## Exact next engineering stage

1. deploy latest active-branch server-side code with updater + backup;
2. update MIPC agent with backup while preserving `device.json`, device ID, key and RDP port;
3. re-measure telemetry cost and subjectively verify RDP micro-freezes are gone or materially reduced;
4. live-test `НАБЛЮДАТЬ 60с` -> detailed telemetry -> automatic stop;
5. fresh install on Windows Server;
6. fresh patched install from Win10 x64 + x86 PowerShell for final Sysnative installer acceptance;
7. only then decide whether PR #19 is ready to merge.

## Do not repeat without a regression reason

- basic proof that OpenSSH reverse RDP works;
- real external RDP baseline;
- Windows reboot recovery baseline;
- OFF/ON behavioral baseline;
- Win10 `Sysnative` native OpenSSH visibility/probe;
- existing-install guard test;
- server endpoint CLOSED/OPEN truth on the already-tested build;
- RDP channel signatures for direct vs Hermes.

## Continuous checkpoint rule

Update this file **during the chat**, not only before migration, whenever any of these changes:

- active PR/branch/head or release target;
- what is actually deployed;
- a bug moves between hypothesis / confirmed / fixed / accepted;
- a live PASS/FAIL changes the next step;
- the exact engineering target changes;
- a risky deployment/update is about to start and the current rollback point matters.

Do not record raw command transcripts here. Record only durable operational truth.