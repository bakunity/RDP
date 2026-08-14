# Hermes RDP — Milestone History

Updated: 2026-08-14

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

The design goal is stronger than cross-chat handoff: losing the current chat, accumulating months of history, or changing implementation should not make current project truth ambiguous.

## 2026-08-13 — v1.2 stabilization acceptance completed

The stabilization cycle closed the major runtime reliability and lifecycle work:

- control-plane deadlock/stale-state fixes;
- Win10 x64 + x86 PowerShell/Sysnative support;
- Windows Server 2019 acceptance;
- reboot/reconnect and multi-device isolation;
- device security/revocation/port reuse;
- transactional server and Windows updates with automatic rollback;
- bounded existing-device Repair with rollback;
- Telegram Repair and new pairing-code UX.

## 2026-08-13 — v1.2.1 published after release packaging hotfix

The first `v1.2.0` publication exposed a release-workflow packaging flaw: tag resolution followed the commit that changed `VERSION`, not the complete release tree. The published `v1.2.0` tag was left immutable.

`v1.2.1` was then published as the stable patch release with synchronized version metadata, full release tree and restored rich product README. The full README again includes badges/links, product architecture, quick start, update/repair and security sections.

A follow-up branch prepares release tagging against the exact validated workflow `HEAD` so future releases cannot repeat this failure mode.

## 2026-08-14 — Trusted RDP certificate phase begins

The next product phase targeted removing the Microsoft Remote Desktop trust warning without adding a domain solely for appearance.

Direction:

- use a publicly trusted certificate matching the existing public IP;
- keep HTTPS/API TLS separate from the Windows RDP listener certificate;
- issue and renew server-side;
- bind/test first on a non-critical Windows fixture with rollback.

## 2026-08-14 — Trusted public-IP RDP + automatic rotation live accepted

The certificate phase reached bounded end-to-end acceptance:

- Let’s Encrypt short-lived public-IP certificate issuance and Hermes-owned renewal lifecycle;
- authenticated certificate package delivery to Windows;
- non-exportable Windows private key and `NETWORK SERVICE` ACL;
- trusted CUSTOM RDP listener with Microsoft Remote Desktop trust warning removed;
- correct rollback to Windows default self-signed state and fixed reapply;
- non-secret server certificate-status path;
- separate low-frequency LocalSystem rotation worker outside the main 3-second agent loop;
- automatic recovery from deliberate local self-signed certificate drift;
- external Microsoft RDP remained trusted after automatic recovery.

Two live bugs were caught and resolved during acceptance: default-self-signed rollback must remove the explicit custom binding, and rotation-worker upgrades must handle cross-context global mutex ACLs. PR #30 and PR #31 were merged after CI and live acceptance.

The next gap was product lifecycle integration so fresh install/update/Repair/uninstall manage the accepted rotation companion automatically.

## 2026-08-14 — CERT-013 full Windows lifecycle integration merged

PR #32 merged as `c23c168a7719a31b4958a4eee555828858d0507c` after full bounded live acceptance.

The accepted certificate-rotation companion is now part of ordinary Windows lifecycle behavior:

- Fresh Install automatically stages/validates and applies certificate lifecycle after the OpenSSH runtime becomes healthy;
- transactional Update manages certificate lifecycle before final success while retaining rollback boundaries;
- Repair preserves the previously accepted core identity/recovery logic and recreates missing rotation scaffolding automatically;
- Uninstall removes both the main Hermes runtime and certificate-rotation runtime.

Live gates covered Update and Repair on the established fixture plus a clean Windows 10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled disposable fixture for Fresh Install, real external Microsoft RDP trust and normal Uninstall. Defender remained enabled and no Hermes exclusion was required.

Accepted product/test code head was `e11cf89ed26d551ca92b4010034d6e6792a9266b` with CI #381 PASS; final evidence/privacy head `f868d8b554e4a6e1cb4a07d0625118696e946cda` passed CI #410 before merge.

## 2026-08-14 — v1.3.0 published

The trusted-RDP certificate cycle closed as the backward-compatible **v1.3.0** minor release.

Before publication:

- core docs were reconciled in PR #33 with CI #418 PASS;
- README/public site were reconciled in PR #34 with CI #420 PASS;
- release metadata, concise public notes, full engineering history and stable install/update links were prepared in PR #35;
- final publication head `74834bd741b5b8794a4d0277976ea3650e35f6c2` passed exact-head CI #426 on Linux full release checks and Windows PowerShell 5.1.

PR #35 merged as `a51e942afbd17997a8100d554f8a0b2e50d4baa7`. Release workflow run #30 validated the release tree, created annotated tag `v1.3.0` pointing exactly to that merge commit, published `Hermes RDP v1.3.0`, and `releases/latest` moved to v1.3.0.

The next cycle starts with no open v1.3.0 release blocker. Natural certificate renewal remains a deferred operational observation rather than a release gate.
