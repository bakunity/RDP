# Hermes RDP — Milestone History

Updated: 2026-08-08

Compact project milestones only. Detailed evidence belongs in `EVIDENCE_LEDGER.md`; current work belongs in `ACTIVE_WORK.md`; deep historical reasoning belongs in Git history/archive.

## 2026-08-05 — Multi-PC product shape

Hermes RDP evolved from a single reverse-RDP setup into a self-hosted multi-device system with a Linux controller, per-device endpoints, Telegram pairing/control, telemetry and first `v1.0.x` releases.

## 2026-08-06 — FRP deployment problem -> OpenSSH redesign

Real Windows deployment exposed Microsoft Defender friction with the FRP binary. Product direction changed instead of requiring Defender exclusions.

Active transport became:

- Microsoft system OpenSSH on Windows;
- isolated Hermes sshd on Linux;
- per-device Ed25519 identity;
- server-side endpoint restriction;
- pinned API/SSH trust path.

FRP left the active runtime architecture.

## 2026-08-06 — First clean OpenSSH installation + external RDP PASS

A Windows device paired successfully, received a persistent endpoint, started its Scheduled Task/reverse tunnel and was reached through standard RDP from an external mobile network.

This established the OpenSSH architecture as a working real-world baseline.

## 2026-08-06 — Legacy Windows ACL migration defect discovered

Upgrade over an old protected Hermes/WinMon/FRP directory exposed a recursive-backup ACL failure. Future migration direction became whole-directory archival/rename with scoped ACL fallback.

## 2026-08-06 — v1.1.0 published

`v1.1.0` became the first published OpenSSH transport release.

## 2026-08-07 — Reboot + Telegram OFF/ON behavioral PASS

Live testing confirmed:

- tested Windows reboot -> Hermes recovered -> RDP usable;
- Telegram OFF interrupted active RDP access;
- Telegram ON restored access.

The focus shifted from “does transport work?” to truthful observability/control and reliability.

## 2026-08-07 — Win10 x64 / x86 PowerShell compatibility bug confirmed

Real Win10 x64 launched from 32-bit PowerShell exposed WOW64 redirection: native Microsoft OpenSSH required `Sysnative` probing instead of blindly using `System32` or PATH/Git SSH.

This became a v1.2.0 compatibility item.

## 2026-08-07 — Persistent cross-chat context initialized

Created repository `context/` so project continuity no longer depends entirely on old chat availability.

## 2026-08-08 — State truth + endpoint truth + RDP-channel acceptance

PR #19 stabilization live-validated:

- independent heartbeat / desired / applied / SSH / endpoint state;
- Linux listener as authoritative public endpoint truth;
- OFF=CLOSED / ON=OPEN;
- direct LAN/VPN vs Hermes RDP channel classification;
- existing-install safety guard without identity/key/port loss.

## 2026-08-08 — Telemetry performance regression identified

Real timing showed that heavy 3-second TCP/process diagnostics could consume most of the agent interval and coincided with RDP micro-freezes.

The branch moved to fast/background/on-demand telemetry and an explicit 60-second observation lease. A Windows Server installer ProductType blocker was also found and fixed in code pending live acceptance.

## 2026-08-08 — Continuous project-memory model

Project memory stopped depending on end-of-chat handoff:

- `ACTIVE_WORK.md` became hot operational state;
- `EVIDENCE_LEDGER.md` became durable acceptance evidence;
- checkpoints became event-driven during work;
- context-only checkpoints may be persisted independently of an open product PR.

## 2026-08-08 — Context lifecycle / garbage collection model

The memory system was completed with long-term hygiene rules:

- HOT / WARM / COLD context layers;
- semantic staleness and `SUPERSEDED` retirement;
- evidence scoping and `REVALIDATION REQUIRED` after relevant code changes;
- release evidence rotation;
- soft size budgets and compaction triggers;
- disposable `LAST_SESSION` and single-current `LATEST_AUDIT`;
- archive index/rules;
- concurrent-writer reconciliation;
- batched context checkpoints where tooling permits;
- feature-branch/base drift must be reconciled before merge.

The design goal is now stronger than cross-chat handoff: **losing the current chat, accumulating months of history, or changing implementation should not make current project truth ambiguous.**