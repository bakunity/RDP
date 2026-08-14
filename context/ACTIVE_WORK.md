# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #30 authenticated Windows trusted-certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after full CERT-011 live acceptance.
- PR #31 automatic trusted RDP certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after full bounded CERT-012 live acceptance.
- PR #32 CERT-013 normal Windows lifecycle integration: **MERGED** as `c23c168a7719a31b4958a4eee555828858d0507c` after complete bounded live acceptance.
- Accepted CERT-013 product/test code head before evidence-only commits: `e11cf89ed26d551ca92b4010034d6e6792a9266b`.
- Reconcile CI #381 PASS; final evidence/privacy head CI #410 PASS (Linux full release checks + Windows PowerShell 5.1).

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
- Stage 3 security/device lifecycle;
- transactional Linux and Windows updater rollback;
- bounded Windows Repair success/rollback;
- Defender coexistence;
- trusted public-IP certificate CERT-001 through CERT-012 bounded acceptance;
- CERT-013 Update, Repair, clean Fresh Install, external trusted RDP and Uninstall lifecycle acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## CERT-013 — CLOSED / MERGED

Live acceptance covered:

- **Update FULL PASS** on `SEC005 TEST`: identity/config/keys/known_hosts/Device ID/RDP port unchanged; Agent/tunnel/rotation task/trusted listener healthy; final `CERT-013_UPDATE=PASS`.
- **Repair FULL PASS** on `SEC005 TEST`: only rotation task/worker removed; public Repair recreated them without changing identity/port/tunnel/trusted binding; final `CERT-013_REPAIR_LIVE=PASS`.
- **Clean Fresh Install FULL PASS** on disposable Win10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled fixture `DESKTOP-T9N368F`: automatic certificate lifecycle, LocalSystem rotation task SID `S-1-5-18`, trusted CUSTOM listener, one Agent + one Hermes SSH, no Defender exclusion; final `CERT-013_FRESH_INSTALL=PASS`.
- **External Microsoft RDP PASS** through `SERVER_IP_OR_DOMAIN:53394`: connection worked and trusted certificate produced no self-signed warning.
- **Uninstall FULL PASS**: both Hermes tasks absent; Agent/rotation/SSH counts zero; active client directory archived/removed; Defender stayed enabled; final `CERT-013_UNINSTALL=PASS`.

## Immediate next step

1. Delete disposable `CERT013 FRESH` in Telegram to revoke its device token/SSH key and free port `53394`.
2. Begin post-CERT-013 docs/product reconciliation: README/Windows install/update/Repair/website must describe the now-shipped automatic trusted-certificate lifecycle.
3. Decide the next patch/minor release boundary from `docs/releases/UNRELEASED.md`; do not publish automatically.

Natural renewal-driven thumbprint rotation remains a deferred observation; do not force extra production issuance solely for evidence.

Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.