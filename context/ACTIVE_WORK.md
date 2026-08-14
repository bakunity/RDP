# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #32 CERT-013 Windows lifecycle integration: merged as `c23c168a7719a31b4958a4eee555828858d0507c` after complete bounded live acceptance.
- PR #33 core trusted-certificate documentation reconciliation: merged as `636cea40342760d3dd1b9127f41c9e7d07e7b211`; CI #418 PASS.
- PR #34 README/public-site reconciliation: merged as `57004e2d7e047655fd7ab5f4edb931a32cd1dba3`; CI #420 PASS.
- Next release boundary is **v1.3.0**: this is a backward-compatible MINOR capability release, not a v1.2.x patch.
- Draft PR #35 `release: Hermes RDP v1.3.0` is open. Initial atomic release-candidate head `13e2716276177849cb02a42864f824747537d88f`; CI #422 Linux full release checks + Windows PowerShell 5.1 PASS.
- **Do not merge PR #35 without explicit publication approval.** Merge changes `VERSION` in `main` and triggers automatic immutable tag/GitHub Release publication.

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
- bounded Windows Repair success/rollback;
- Defender coexistence;
- trusted public-IP certificate CERT-001 through CERT-012 bounded acceptance;
- CERT-013 Update, Repair, clean Fresh Install, external trusted RDP and Uninstall lifecycle acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## v1.3.0 release candidate

The draft release tree contains:

- version metadata `1.3.0`;
- concise `docs/releases/v1.3.0.md` public notes;
- detailed `docs/releases/history/v1.3.0-full.md` engineering history;
- `CHANGELOG.md` v1.3.0 section;
- `UNRELEASED.md` reset for the post-v1.3.0 cycle;
- README/site/quickstart stable links updated to `v1.3.0`;
- release protocol updated to exact validated-HEAD + release-body synchronization behavior.

No new runtime live acceptance is required solely for the release metadata/presentation cut. Final publication gate is exact-head CI + explicit approval.

## Exact next step

1. Reconcile this context-only `main` checkpoint into PR #35 and rerun CI on the resulting exact release head.
2. Keep PR #35 draft after green CI.
3. Wait for explicit publication approval.
4. On approval: mark ready, merge with exact-head guard, then verify immutable `v1.3.0` tag, GitHub Release body and `releases/latest`.

Natural renewal-driven thumbprint rotation remains a deferred operational observation and is not a v1.3.0 blocker. Do not force extra production issuance solely for evidence.

Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
