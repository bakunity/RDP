# Hermes RDP — Current State Snapshot

Updated: 2026-08-13

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Published release: `v1.1.0`.
- Target: **v1.2.0 — Stabilization**.
- PR #19–#25: merged and accepted.
- PR #26 documentation reconciliation: merged, merge commit `b3e49e9caff0229ce9f626094393fbf1692878de`.
- PR #27 final release PR: draft, not merged.
- PR #27 CI #279: Linux PASS, Windows PowerShell 5.1 PASS.

## Runtime architecture

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd
      |
reverse Microsoft OpenSSH
      |
Windows RDP
      |
persistent endpoint per device
```

Admin SSH remains independent from Hermes tunnel SSH. FRP is not active runtime. Per-device local identity remains separate per Windows client.

## Live deployment truth

- Production controller is still deployed from accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`.
- PR #26 changed documentation only.
- PR #27 is unmerged release metadata/documentation and has not changed production.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason:

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell/Sysnative;
- Telegram OFF/ON/RESTART and automatic dashboard refresh;
- Stage 3 security/device lifecycle acceptance;
- transactional server updater success/rollback;
- transactional Windows updater success/rollback;
- existing-device Repair success/rollback;
- Telegram Repair screen and deterministic new-code retry UX.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains only PARTIAL PASS for its deferred final exact-Windows one-process observation; do not repeat its five-cycle stress test.

## Current release gate

The v1.2 runtime acceptance is complete. Remaining action is publication control:

1. keep PR #27 draft until explicit final release approval;
2. after approval, mark ready and merge the exact CI-passing head;
3. verify `v1.2.0` tag/GitHub Release and release links;
4. then begin the separate RDP trusted-certificate track.
