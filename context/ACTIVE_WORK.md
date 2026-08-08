# Hermes RDP — Active Work

Updated: 2026-08-08 23:57 +03:00

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- PR head at this checkpoint: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- Draft release notes: `docs/releases/v1.2.0-draft.md` on the active branch.
- Product code from PR #19 is still unmerged.

## Live-confirmed baseline

Detailed proof lives in `EVIDENCE_LEDGER.md`.

Confirmed on tested builds:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- Telegram OFF interrupts RDP / ON restores it;
- server-authoritative endpoint CLOSED/OFF and OPEN/ON;
- state model separates heartbeat, desired/applied access, SSH and endpoint;
- direct LAN/VPN RDP classified as Hermes=0/direct=1;
- Hermes RDP classified as Hermes=1/direct=0;
- open endpoint alone did not count as active Hermes RDP;
- existing-install guard preserves task/identity/key/port;
- Win10 x64 under x86 PowerShell can reach native Microsoft OpenSSH through `Sysnative`.

Important: RDP classification/ON-OFF/SSH-process baselines were accepted **before the latest low-cost telemetry/main-loop refactor**. They now have explicit current-head revalidation rows in `EVIDENCE_LEDGER.md`; do not automatically transfer the old PASS to the newest agent.

## Confirmed current bugs/regressions

### Telemetry performance regression

Before optimization on MIPC:

```text
full Established TCP query  ~1059 ms
RDP-only TCP query          ~516 ms
full Win32_Process query    ~357 ms
TopProcesses sample         800 ms minimum
```

The old 3-second telemetry loop could spend most of its interval collecting diagnostics and coincided with RDP micro-freezes.

Status: **CONFIRMED REGRESSION; FIX IMPLEMENTED; CURRENT-HEAD LIVE ACCEPTANCE PENDING**.

### Windows Server installer gate

Real Windows Server install was blocked by the old `ProductType != 1` client-only check despite later code mentioning Server.

Status: **CONFIRMED BUG; FIX IMPLEMENTED; REAL FRESH INSTALL PENDING**.

## Implemented on PR head — not yet runtime-accepted

### Low-cost telemetry model

```text
FAST ~3s
heartbeat / commands / access / SSH / RDP channel

BACKGROUND ~15s
CPU / RAM / disk / network / sessions / route / uptime

OBSERVE 60s
resources ~3s
TOP processes ~6s
Telegram live render ~3s
then automatic stop
```

Also implemented:

- no background TOP-process scan;
- full Established TCP-table scan removed from RDP classifier;
- RDP query narrowed to port 3389 + exact peer lookup only for loopback;
- SSH process query narrowed/reused inside cycle;
- permanent Telegram AUTO 3s replaced by explicit `НАБЛЮДАТЬ 60с` lease;
- Russian user-facing status vocabulary;
- Windows Server ProductType 2/3 support.

Latest branch CI at this checkpoint is green. CI is not runtime acceptance.

## Deployment truth

- A **pre-performance-refactor** PR build is live on the working server and passed state/endpoint/RDP-channel acceptance.
- The newest low-cost telemetry / observation / Windows Server changes are **not yet considered live-deployed or accepted**.
- MIPC is still the live acceptance device for the next agent update.

## Current-head revalidation gate

After deploying/updating the newest build, revalidate only behavior touched by the refactor:

1. exactly one Hermes `ssh.exe` in normal ON state;
2. OFF command is still received/applied and endpoint becomes CLOSED;
3. ON restores one tunnel and endpoint OPEN;
4. direct LAN/VPN RDP still reports Hermes=0/direct=1;
5. Hermes RDP still reports Hermes=1/direct=0;
6. open endpoint with no Hermes RDP client still reports Hermes=0.

These are regression smoke tests, not a re-run of the whole historical acceptance matrix.

## Exact next engineering stage

1. deploy latest PR server-side code with updater + backup;
2. update MIPC agent with backup while preserving `device.json`, device ID, SSH key and assigned RDP port;
3. re-measure telemetry cost and subjectively verify RDP micro-freezes disappear or materially reduce;
4. run the current-head regression smoke above;
5. test `НАБЛЮДАТЬ 60с`: detailed resources/processes appear, then heavy telemetry + 3s Telegram redraw stop automatically;
6. fresh install on real Windows Server;
7. fresh patched install from Win10 x64 + x86 PowerShell for final Sysnative e2e acceptance;
8. synchronize/reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
9. merge only after the acceptance gate is green or explicitly split with evidence boundaries.

## PR/base drift note

Continuous context-only commits have advanced `main` while PR #19 remains based on older `main`.

Current comparison at this checkpoint:

```text
main vs fix/control-state-dashboard: diverged
PR branch ahead: 33 commits
PR branch behind: 39 commits
```

GitHub currently reports PR `mergeable: false`. Do **not** treat that alone as a confirmed product-code conflict yet. Before merge:

- reconcile current `main` into/rebase the feature branch;
- resolve any actual conflicts if present;
- rerun CI on the reconciled branch;
- recheck mergeability.

Future context checkpoints should batch related multi-file context changes into one commit where possible to reduce default-branch history noise/base drift.

## Do not repeat without regression reason

- basic proof that OpenSSH reverse RDP architecture works;
- historical external-network RDP baseline;
- Windows reboot baseline;
- raw Sysnative visibility/probe diagnosis;
- existing-install guard baseline.

For behavior explicitly listed in the current-head revalidation gate, perform only the targeted smoke after the new agent is live.

## Context state

The project-memory system now has:

- continuous event-driven checkpoints;
- HOT/WARM/COLD layers;
- evidence scoping + revalidation obligations;
- stale/superseded context retirement;
- soft size budgets + release-boundary compaction;
- archive policy;
- canonical owner per fact.

See `CONTEXT_LIFECYCLE.md`. Context itself is now a maintained subsystem, not an append-only notebook.