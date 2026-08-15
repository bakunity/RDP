# Hermes RDP — Current State Snapshot

Updated: 2026-08-15

For immediate operational truth read `ACTIVE_WORK.md`; for detailed current evidence read `EVIDENCE_LEDGER.md`.

## Repository / release

- Current stable published release: **v1.3.0**; tag/history remain immutable.
- Active development PR: **#37 `feat: add zero-config server installer`**.
- Runtime-accepted code boundary: `056bf7473ff851157f4c749f233fb0fb8b57a133`.
- CI #459 on that exact head passed Linux full release checks and Windows PowerShell 5.1.
- PR #37 is not merged; merge requires explicit user approval.

## Runtime architecture

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

Admin SSH remains independent. FRP is not active runtime. Certificate rotation remains a separate low-frequency path outside the main Agent loop.

## Zero-config server onboarding boundary

PR #37 normal-user flow:

```text
curl installer
→ validate/repair supported APT state
→ detect public IPv4
→ masked Telegram bot token with bounded retry
→ secure private one-time owner claim
→ exact source archive
→ core Hermes install
→ automatic trusted RDP certificate lifecycle
→ Telegram /start
```

Live Debian 13 Trixie acceptance now confirms:

- stale Debian archive repair with backup;
- safe semantic normalization of overlapping simple APT source component sets, with rollback protection;
- clean APT preflight on the subsequent install;
- public IPv4 discovery;
- masked Telegram token entry and successful bot validation;
- secure private owner claim before core mutation;
- normal `/start` dashboard;
- exact source archive resolution;
- full clean-state Hermes reinstall from exact head `056bf7473ff851157f4c749f233fb0fb8b57a133`;
- dedicated sshd/controller active and `=== HERMES RDP READY ===`;
- safe coexistence with existing nginx on TCP 80;
- direct ACME challenge `alias` and bounded reload readiness;
- previously accepted staging + production short-lived public-IP issuance;
- fresh reinstall reusing valid preserved certificate lineage without forced reissuance;
- active/enabled Hermes renewal timer, smoke `PASS_NOT_DUE`, package/state helpers ready and `TRUSTED_RDP_CERT=PASS`.

An interruption while waiting for owner claim after a clean purge left no partially installed Hermes core; rerunning the normal installer succeeded because claim precedes core mutation.

## Accepted compatibility baseline

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, transactional updater rollback, existing-device Repair, Defender coexistence, and CERT-001 through CERT-013.

Natural renewal-driven thumbprint rotation remains deferred until the real next renewal. SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture observation.

## Exact next step

Remove the temporary clean-reinstall acceptance helper, run final CI on the resulting exact head and mark PR #37 ready for review. Merge only after explicit user approval and expected-head verification.
