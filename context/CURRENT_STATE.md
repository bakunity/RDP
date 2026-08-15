# Hermes RDP — Current State Snapshot

Updated: 2026-08-15

For immediate operational truth read `ACTIVE_WORK.md`; for detailed current evidence read `EVIDENCE_LEDGER.md`.

## Repository / release

- Current stable published release: **v1.3.0**; tag/history remain immutable.
- PR #37 `feat: add zero-config server installer` is **ready for review** and not merged.
- Runtime-accepted product-code boundary: `056bf7473ff851157f4c749f233fb0fb8b57a133`; CI #459 PASS.
- Acceptance/context cleanup commit `ff264100b231c3f90269c3e8fa17bda5e4d2aab2` removed the temporary clean-reinstall helper and passed CI #460.
- Merge requires explicit user approval and green CI on the current exact head.

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

PR #37 normal-user flow is live accepted on Debian 13 Trixie:

- APT stale-source recovery with backup;
- semantic normalization of overlapping simple `deb`/`deb-src` component sets with validation/rollback;
- public IPv4 discovery;
- masked Telegram bot-token entry and successful validation;
- secure private one-time owner claim before core mutation;
- normal `/start` dashboard;
- immutable source archive resolution;
- full clean-state Hermes reinstall;
- dedicated sshd/controller active and `=== HERMES RDP READY ===`;
- existing nginx preserved on TCP 80;
- direct ACME challenge `alias` and bounded reload readiness;
- accepted staging/production short-lived public-IP certificate issuance;
- fresh reinstall reusing valid preserved certificate lineage without forced reissuance;
- active/enabled renewal timer, smoke `PASS_NOT_DUE`, package/state helpers ready and `TRUSTED_RDP_CERT=PASS`.

Closing the terminal while waiting for the owner claim after a clean purge left no partially installed core. Re-running the normal installer succeeded.

## Accepted compatibility baseline

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, transactional updater rollback, existing-device Repair, Defender coexistence, and CERT-001 through CERT-013.

Natural renewal-driven thumbprint rotation remains deferred until the real next renewal. SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture observation.

## Exact next step

Wait for explicit user approval to merge PR #37. Immediately before merge, verify expected current head and green required CI. Do not alter v1.3.0 historical tags.
