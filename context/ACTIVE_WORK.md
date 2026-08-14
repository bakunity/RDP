# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #30 authenticated Windows trusted-certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after full CERT-011 live acceptance.
- PR #31 automatic trusted RDP certificate rotation: **merged** as `bd25db552aae8303356953fe2807a7bd855cba95` after full bounded CERT-012 live acceptance.
- Final tested PR #31 head: `14da128328589dfae6c8e3b6819977120be16739`; CI #353 Linux full release checks PASS + Windows PowerShell 5.1 PASS.
- Linux production runtime is deployed on earlier compatible PR #31 server head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`; later PR #31 changes were Windows worker/setup/test fixes.
- `SEC005 TEST` currently has the final PR #31 Windows rotation worker and trusted CUSTOM RDP binding active.

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

The certificate worker is deliberately separate from the performance-sensitive 3-second main agent loop.

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
- trusted public-IP certificate CERT-001 through CERT-012 bounded acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted public-IP RDP certificate — COMPLETE bounded acceptance

User decision: keep the current public-IP Let’s Encrypt certificate representation as-is; no domain/CN cosmetic work is pending.

CERT-011 and CERT-012 are live accepted on non-critical `SEC005 TEST`:

- authenticated trusted certificate package delivery/import/binding PASS;
- correct type-aware rollback to Windows default self-signed PASS;
- fixed trusted reapply PASS;
- server non-secret certificate status/renewal path PASS;
- separate LocalSystem rotation task PASS (`S-1-5-18`), including Russian localized `СИСТЕМА` identity handling;
- global mutex upgrade bug reproduced, rollback succeeded, fix CI/live accepted;
- controlled self-signed drift was detected by the scheduled worker;
- worker invoked sync itself, logged `CERT_ROTATION=UPDATED`, restored the expected CUSTOM trusted binding, kept TCP 3389 listening and remained Running;
- a fresh external Microsoft Remote Desktop connection after automatic recovery succeeded as protected/trusted with no self-signed warning.

Natural renewal-driven thumbprint rotation remains **post-merge observation only**. Do not force extra production issuance solely to test it.

## Active work — CERT-013 normal Windows lifecycle integration

Goal: remove the manual `setup-client-cert-rotation.ps1` step from normal product use.

Next implementation must integrate the already accepted certificate companion into the ordinary Windows lifecycle:

1. fresh install: after device identity/config exists, install/update the certificate rotation worker transactionally and allow its initial check to bind trusted cert when the server enables it;
2. transactional update: update worker + sync companion with the same immutable SHA and rollback them/task together with the main client update;
3. Repair: restore missing/broken rotation files/task without rotating device identity or weakening Defender;
4. uninstall: remove Hermes-owned rotation task/files while preserving only data that current uninstall policy intentionally preserves;
5. preserve Win10 PowerShell 5.1 and x86 -> Sysnative compatibility;
6. keep certificate work outside the 3-second main agent loop;
7. add Linux/static + Windows PowerShell 5.1 regression gates before live acceptance.

## Exact next action

Create a new branch from current `main` for CERT-013, inspect `install-client.ps1`, `update-client.ps1`, `repair-client.ps1` and `uninstall-client.ps1`, then implement lifecycle integration without changing already accepted transport/control behavior.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
