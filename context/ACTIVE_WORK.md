# Hermes RDP — Active Work

Updated: 2026-08-09

Purpose: first operational file after `context/README.md`. Contains current work only; completed/superseded detail belongs elsewhere.

## Active development

- Active PR: **#19 — `fix: stabilize control state and Windows OpenSSH detection`**.
- Active branch: `fix/control-state-dashboard`.
- Acceptance head: `586e9446ea41262f1ed0d9c84ba72838a47d9bc5`.
- Published release: `v1.1.0`.
- Target release: **v1.2.0 — Stabilization**.
- Product code from PR #19 is still unmerged.

## Deployment truth

The exact immutable acceptance head `586e9446ea41262f1ed0d9c84ba72838a47d9bc5` is now deployed server-side and installed on the MIPC Windows agent.

Server updater result:

- both Hermes services returned `active`;
- rollback backup created under `/var/backups/hermes-rdp/`.

MIPC agent update result:

- Scheduled Task = `Running`;
- `device_id` unchanged;
- assigned RDP port unchanged (`53389` on this acceptance device);
- `device.json` hash unchanged;
- private SSH key hash unchanged;
- exactly one Hermes `ssh.exe` after update;
- local rollback copy created under `C:\ProgramData\HermesRDP\backups\`.

This proves deployment/provenance and identity-preserving update. It does **not** yet prove performance, OFF/ON, RDP classification or observation behavior on the new head.

## Stable live baseline

Detailed evidence lives in `EVIDENCE_LEDGER.md`.

Do not re-prove wholesale:

- OpenSSH reverse RDP end-to-end;
- external-network RDP;
- tested Windows reboot recovery;
- existing-install guard;
- raw Win10 x64 + x86 PowerShell `Sysnative` visibility/probe;
- earlier state/endpoint/RDP classification baseline.

Relevant baseline behaviors touched by the latest telemetry/main-loop refactor remain under targeted revalidation.

## Confirmed regression being accepted

Before optimization on MIPC:

```text
full Established TCP query  ~1059 ms
RDP-only TCP query          ~516 ms
full Win32_Process query    ~357 ms
TopProcesses sample         800 ms minimum
```

The old 3-second telemetry loop could spend most of its interval collecting diagnostics and coincided with RDP micro-freezes.

Latest head implements:

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

Background TOP-process collection is removed; RDP TCP queries are narrowed; SSH process discovery is filtered/reused.

Status: **IMPLEMENTED + DEPLOYED; LIVE PERFORMANCE ACCEPTANCE PENDING**.

## Windows Server

Confirmed old bug: installer rejected Windows Server through the client-only ProductType gate.

Latest head allows ProductType 2/3 and has regression coverage.

Status: **IMPLEMENTED + DEPLOYED SERVER-SIDE; REAL FRESH WINDOWS SERVER INSTALL PENDING**.

## Exact next engineering stage

1. measure the cost of the new MIPC fast/background paths and compare with the old measurements;
2. subjectively verify whether RDP micro-freezes disappear or materially reduce;
3. targeted current-head smoke:
   - one Hermes `ssh.exe`;
   - OFF -> applied OFF + endpoint CLOSED;
   - ON -> one tunnel + endpoint OPEN;
   - direct LAN/VPN RDP -> Hermes=0/direct=1;
   - Hermes RDP -> Hermes=1/direct=0;
   - endpoint open with no Hermes RDP client -> Hermes=0;
4. test `НАБЛЮДАТЬ 60с`: heavy telemetry appears, then automatic stop and no endless 3-second redraw;
5. real fresh Windows Server install;
6. fresh patched install from Win10 x64 + PowerShell x86 for final Sysnative e2e acceptance;
7. reconcile PR #19 with current `main`, rerun CI and recheck mergeability;
8. merge only after the acceptance gate is green or explicitly split with evidence boundaries.

## PR/base drift

Context-only commits have advanced `main` while product code remains in PR #19. Before merge, query current divergence, reconcile the feature branch with current `main`, rerun CI and recheck mergeability. Do not keep exact ahead/behind counts as durable facts.

## Context rule

Checkpoint meaningful PASS/FAIL/root-cause/deployment transitions continuously. Record outcomes, not terminal transcripts. See `SESSION_PROTOCOL.md` and `CONTEXT_LIFECYCLE.md`.