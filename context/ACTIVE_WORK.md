# Hermes RDP — Active Work

Updated: 2026-08-15

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.3.0**; historical tag/history remain immutable.
- Active product PR: **#37 `feat: add zero-config server installer`**.
- Runtime-accepted code boundary: `056bf7473ff851157f4c749f233fb0fb8b57a133`.
- CI #459 on that exact head: Linux full release checks PASS and Windows PowerShell 5.1 PASS.
- PR #37 must not be merged without explicit user approval.

## Stable architecture

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd :7000
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent endpoint per device
```

Trusted-RDP certificate lifecycle remains a separate low-frequency path and stays outside the 3-second Agent loop.

## Accepted baseline — do not repeat without regression evidence

- external Microsoft RDP through Hermes;
- simultaneous multi-device operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell / Sysnative OpenSSH compatibility;
- Telegram OFF/ON/RESTART and status UX;
- transactional Linux and Windows updater rollback;
- existing-device Repair success/rollback;
- Defender coexistence without exclusions/disablement;
- trusted public-IP certificate lifecycle CERT-001 through CERT-013.

## Current work — PR #37 zero-config server onboarding

Normal-user flow:

```text
one curl command
→ Debian/Ubuntu + APT preflight/repair
→ public IPv4 detection
→ masked Telegram bot-token input
→ private one-time /claim owner binding
→ immutable source resolution
→ core Hermes install
→ automatic trusted public-IP certificate lifecycle
→ Telegram /start
```

### Live acceptance on Debian 13 Trixie

- stale `archive.debian.org` repair with backup: **PASS**;
- overlapping APT component cleanup with backup/revalidate/rollback: **PASS on the acceptance fixture**; subsequent install reports clean APT repositories;
- bootstrap dependencies and public IPv4 discovery: **PASS**;
- masked Telegram token display: **PASS**;
- `getMe`, webhook-free validation and secure private owner claim: **PASS**;
- normal `/start` dashboard: **PASS**;
- immutable source archive resolution: **PASS**;
- full clean-state reinstall from exact head `056bf7473ff851157f4c749f233fb0fb8b57a133`: **PASS**;
- dedicated Hermes sshd active and controller active: **PASS**;
- installer reached `=== HERMES RDP READY ===`: **PASS**;
- existing nginx on TCP 80 preserved: **PASS**;
- nginx ACME route/direct `alias` live probes: **PASS**;
- prior staging + production public-IP issuance through nginx webroot: **PASS**;
- fresh reinstall reused valid preserved lineage and re-established lifecycle without forced issuance: **PASS**;
- renewal timer active/enabled, smoke `PASS_NOT_DUE`, package/state helpers ready, `TRUSTED_RDP_CERT=PASS`: **PASS**.

### Resolved bugs found during acceptance

- Telegram JSON shell default corruption;
- source-archive executable mode mismatch;
- nginx TCP-80 coexistence;
- inaccessible ACME webroot location;
- live 404 from `root + try_files`, replaced by direct `alias`;
- nginx reload readiness race;
- overlapping APT component sets that produced duplicate-target warnings despite non-identical source lines;
- invisible Telegram token entry and immediate abort on empty/invalid input. Token input is now masked; bounded retry is CI-covered.

### Interruption behavior

During the clean-room test the terminal was closed while waiting for the owner claim. Because claim occurs before core mutation, no partially installed Hermes core remained; rerunning the normal installer from the clean state succeeded. Treat this as accepted interruption behavior for that stage.

## Exact next action

Remove the temporary clean-reinstall acceptance helper, checkpoint final evidence/context, run CI on the resulting exact head, then mark PR #37 ready for review. Merge only after explicit user approval and expected-head verification.

Natural renewal-driven certificate rotation remains a deferred operational observation, not a blocker. SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture one-process observation.

Never store bot tokens, private keys, PFX passwords, device/API tokens, one-time claim/pair codes, unnecessary production IPs, certificate package secrets or personal numeric IDs in context.
