# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #30 authenticated Windows trusted-certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after full CERT-011 live acceptance.
- PR #31 automatic trusted RDP certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after full bounded CERT-012 live acceptance.
- PR #32 CERT-013 Windows lifecycle integration has completed all bounded live gates. Accepted code head before evidence-only commits: `e11cf89ed26d551ca92b4010034d6e6792a9266b`.
- PR #32 reconcile CI #381: Linux full release checks PASS + Windows PowerShell 5.1 PASS.
- CERT-013 Update + Repair were live accepted on `SEC005 TEST`.
- CERT-013 clean Fresh Install + external trusted RDP + Uninstall were live accepted on disposable Win10 fixture `DESKTOP-T9N368F`.

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

Certificate work remains outside the performance-sensitive 3-second main agent loop.

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
- CERT-013 Update, Repair, Fresh Install, external trusted RDP and Uninstall lifecycle acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## CERT-013 — normal Windows lifecycle integration

Goal: no separate manual certificate-rotation setup in normal product use.

### Code / CI

PR #32 accepted code head `e11cf89ed26d551ca92b4010034d6e6792a9266b`:

- fresh install stages/parses Agent + certificate setup from one immutable SHA before pairing/runtime mutation;
- transactional Update composes certificate setup as a nested transactional sub-operation before final `UPDATE=PASS`;
- previously accepted Repair implementation is preserved byte-for-byte as `repair-client-core.ps1`; public `repair-client.ps1` wraps it with certificate lifecycle management and outer Agent/task snapshot rollback;
- uninstall stops/unregisters both Hermes Agent and certificate-rotation tasks/processes;
- historical Repair assertions remain attached to the unchanged core; new CERT-013 tests cover wrapper/lifecycle composition;
- reconcile with current `main` touched only release/context/workflow files outside the eight CERT-013 product/test files;
- CI #381: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

### Live acceptance on `SEC005 TEST`

**Transactional Update = FULL PASS**:

- certificate worker returned `CERT_ROTATION=UNCHANGED` and `CERT-012_SETUP=PASS`;
- `UPDATE=PASS` + `CertificateRotation: managed`;
- `device.json`, private/public SSH keys, `known_hosts`, Device ID and RDP port unchanged;
- main task Running, exactly one Agent and one Hermes `ssh.exe`;
- rotation task Running as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM RDP binding and TCP 3389 preserved;
- final `CERT-013_UPDATE=PASS`.

**Repair lifecycle = FULL PASS**:

- test removed only rotation Scheduled Task + worker file; identity, RDP binding and device registration stayed intact;
- public Repair returned core `REPAIR=PASS` and wrapper `CERT-013_REPAIR=PASS`;
- identity/config/SSH keys/known_hosts/RDP port unchanged;
- main Agent/tunnel healthy after Repair;
- rotation worker + task recreated; task runs as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM RDP binding unchanged; TCP 3389 stayed listening;
- final `CERT-013_REPAIR_LIVE=PASS`.

### Disposable clean fixture acceptance

Fixture: `DESKTOP-T9N368F`, Windows 10 Pro build 19045 x64, Windows PowerShell 5.1 x64, Defender AV + real-time protection enabled, Hermes absent before test, OpenSSH Client already installed.

**Fresh Install = FULL PASS** from exact accepted code head `e11cf89e...`:

- `CERT_ROTATION=UPDATED`, `CERT-012_SETUP=PASS`;
- device `CERT013 FRESH` registered on endpoint `150.241.94.110:53394`;
- main Agent Running, exactly one Agent + one Hermes SSH process;
- rotation task Running as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM RDP thumbprint `2E170C609B47E0D34F16238503998509EDDDC79C` bound; TCP 3389 listening;
- Defender stayed enabled with no Hermes exclusion;
- final `CERT-013_FRESH_INSTALL=PASS`.

**External Microsoft RDP = PASS**:

- real external connection to `150.241.94.110:53394` succeeded;
- trusted certificate accepted with no self-signed warning.

**Uninstall = FULL PASS**:

- both Hermes tasks absent;
- main Agent, rotation worker and Hermes SSH process counts all zero;
- active `C:\ProgramData\HermesRDP` absent;
- archive created at `C:\ProgramData\HermesRDP.removed.20260814-132332` and validated;
- Defender real-time protection stayed enabled;
- final `CERT-013_UNINSTALL=PASS`.

## Immediate next step

1. Let final evidence-only PR head CI finish green.
2. Mark PR #32 ready and merge with exact-head guard.
3. Delete disposable `CERT013 FRESH` device in Telegram to revoke its token/key and free port `53394`.
4. Update context to the merged commit and move to the next product gap.

Natural renewal-driven thumbprint rotation remains a deferred observation; do not force extra production issuance solely for evidence.

Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
