# Hermes RDP — Active Work

Updated: 2026-08-15

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.3.0**.
- v1.3.0 release tag/history remain immutable and unchanged.
- Active product PR: **#37 `feat: add zero-config server installer`**.
- PR #37 is still draft and must not be merged before the remaining bounded live checks are closed.
- Latest runtime-accepted code boundary before this context checkpoint: `0aa6bed193abcd6ef60673304695e7565d697011`; CI #453 PASS on Linux full release checks and Windows PowerShell 5.1.

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

## Current work — zero-config server onboarding

PR #37 introduces the normal-user server path:

```text
one curl command
→ Debian/Ubuntu + APT preflight
→ public IPv4 detection
→ hidden Telegram bot-token input
→ private one-time /claim owner binding
→ immutable source resolution
→ core Hermes install
→ automatic trusted public-IP certificate attempt
→ ready for Telegram /start
```

### Live acceptance on Debian 13 Trixie

- known stale `archive.debian.org` source detected and repaired with backup: **PASS**;
- bootstrap dependencies: **PASS**;
- public IPv4 discovery: **PASS**;
- Telegram `getMe` and webhook-free validation: **PASS**;
- secure private one-time `/claim` owner binding: **PASS**;
- immutable GitHub source archive resolution: **PASS**;
- core Hermes install: **PASS**;
- dedicated Hermes sshd active: **PASS**;
- controller active: **PASS**;
- installer reached `=== HERMES RDP READY ===`: **PASS**;
- existing nginx on TCP 80 preserved: **PASS**;
- dedicated nginx ACME route and challenge `alias`: live HTTP 200 probe **PASS**;
- Let's Encrypt staging short-lived public-IP issuance through nginx webroot: **PASS**;
- Let's Encrypt production short-lived public-IP issuance through nginx webroot: **PASS**;
- Hermes renewal timer active/enabled: **PASS**;
- renewal smoke `PASS_NOT_DUE`: **PASS**;
- certificate package/state helpers ready: **PASS**;
- final `TRUSTED_RDP_CERT=PASS`: **PASS**.

### Confirmed bugs found and resolved during live acceptance

- Bash default Telegram JSON payload produced an extra `}`: resolved + regression test.
- GitHub archive scripts were not executable: resolved by repository executable mode + regression test.
- existing nginx on TCP 80 blocked standalone ACME: resolved with bounded nginx-webroot mode.
- ACME webroot was initially placed under private Hermes state: resolved to `/var/www/hermes-rdp-acme`.
- nginx `root + try_files` challenge mapping returned 404 on the live fixture: resolved to direct `alias`, live route/file probe PASS.
- immediate probe after `systemctl reload nginx` raced old workers: resolved with bounded readiness retries; CI #453 PASS.
- exact duplicate APT source lines produced warning spam: cleanup logic implemented with backup/revalidate/rollback and CI coverage.

## Remaining bounded checks

1. Send `/start` to the newly configured Telegram bot and confirm the normal Hermes dashboard opens for the claimed owner.
2. Clean the already-existing duplicate APT entries on this fixture and confirm `apt-get update` no longer emits `configured multiple times`; do not rerun the whole Hermes install for this.
3. Update evidence/context after those two checks and run final CI.
4. Mark PR #37 ready only after the above checks pass. Merge only after explicit user approval and with expected-head protection.

Natural renewal-driven certificate rotation remains a **deferred operational observation**, not a blocker. Do not force extra production issuance solely for evidence.

SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture one-process observation.

Never put private keys, PFX passwords, API/device tokens, pairing/claim codes, unnecessary production IPs or personal numeric IDs into context/chat.
