# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #30 authenticated Windows trusted-certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after full CERT-011 live acceptance.
- PR #31 automatic trusted RDP certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after full bounded CERT-012 live acceptance.
- PR #32 CERT-013 Windows lifecycle integration is **OPEN / DRAFT / mergeable** on head `29c19182ef99497b4cc314e3b4e9b6598ad95516`.
- PR #32 CI #363: Linux full release checks PASS + Windows PowerShell 5.1 PASS.
- `SEC005 TEST` has live-accepted CERT-013 transactional Update and Repair lifecycle behavior on exact head `29c19182...`.

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
- trusted public-IP certificate CERT-001 through CERT-012 bounded acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## CERT-013 — normal Windows lifecycle integration

Goal: no separate manual certificate-rotation setup in normal product use.

### Code / CI

PR #32 head `29c19182ef99497b4cc314e3b4e9b6598ad95516`:

- fresh install stages/parses Agent + certificate setup from one immutable SHA before pairing/runtime mutation;
- transactional Update composes the certificate setup as a nested transactional sub-operation before final `UPDATE=PASS`;
- previously accepted Repair implementation is preserved byte-for-byte as `repair-client-core.ps1`; public `repair-client.ps1` wraps it with certificate lifecycle management and outer Agent/task snapshot rollback;
- uninstall stops/unregisters both Hermes Agent and certificate-rotation tasks/processes;
- historical Repair assertions remain attached to the unchanged core; new CERT-013 tests cover wrapper/lifecycle composition;
- CI #363: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

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

- test removed only rotation Scheduled Task + worker file; identity, RDP binding and device registration were not changed;
- public Repair returned accepted core `REPAIR=PASS` and wrapper `CERT-013_REPAIR=PASS`;
- identity/config/SSH keys/known_hosts/RDP port unchanged;
- main Agent/tunnel remained healthy after Repair;
- rotation worker + task were recreated and task runs as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM RDP binding remained exactly unchanged; TCP 3389 stayed listening;
- final `CERT-013_REPAIR_LIVE=PASS`.

Do not destructively test uninstall/fresh install on `SEC005 TEST`.

## Remaining CERT-013 merge gate

Run **fresh install -> verify -> uninstall** only on a separate disposable supported Windows fixture/VM.

Required fresh-install acceptance:

1. ordinary installer completes pairing and OpenSSH tunnel;
2. installer automatically creates/starts certificate rotation companion without manual certificate setup;
3. trusted CUSTOM RDP listener is active and TCP 3389 listens;
4. external Microsoft RDP works;
5. uninstall removes both Hermes tasks/processes and archives/removes active Hermes client directory according to current uninstall behavior;
6. disposable fixture may then be discarded.

If no disposable fixture is available, leave PR #32 draft rather than risking `SEC005 TEST`.

Natural renewal-driven thumbprint rotation remains a deferred observation; do not force extra production issuance solely for evidence.

Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
