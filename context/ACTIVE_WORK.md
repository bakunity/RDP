# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.3.0**.
- PR #35 merged as `a51e942afbd17997a8100d554f8a0b2e50d4baa7` after final exact-head CI #426 PASS.
- Annotated tag `v1.3.0` points to that exact merge commit.
- Release workflow run #30 completed successfully and published `Hermes RDP v1.3.0`.
- GitHub `releases/latest` resolves to `v1.3.0`.
- No active product PR is currently required for the release.

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

Trusted-RDP certificate side path:

```text
Hermes cert renew timer
      |
non-secret cert state/status
      |
authenticated Windows SYSTEM rotation worker
      |
PFX sync only on thumbprint change / local drift
      |
Windows RDP CUSTOM trusted certificate
```

Certificate work remains outside the performance-sensitive 3-second main Agent loop.

## Accepted baseline — do not repeat without regression evidence

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell / Sysnative OpenSSH compatibility;
- Telegram OFF/ON/RESTART and status UX;
- transactional Linux and Windows updater rollback;
- bounded existing-device Repair success/rollback;
- Defender coexistence without exclusions/disablement;
- trusted public-IP certificate lifecycle CERT-001 through CERT-013, including Fresh Install/Update/Repair/Uninstall integration and trusted external RDP.

Detailed v1.3.0 acceptance is frozen in `context/archive/releases/v1.3.0-evidence.md` and `docs/releases/history/v1.3.0-full.md`.

## Current work

The v1.3.0 release cycle is closed. No release blocker remains.

Natural renewal-driven certificate rotation is a **deferred operational observation**, not a blocker. Do not force extra production issuance solely for evidence.

## Exact next step

When the current short-lived production certificate renews naturally, capture only bounded non-secret evidence that server state updates, Windows rotates automatically and a fresh Microsoft RDP connection remains trusted.

If starting a new product feature before that natural event, select and scope the next workstream explicitly rather than reopening accepted v1.3.0 tests.

SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture one-process observation.

Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
