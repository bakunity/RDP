# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md` / `EVIDENCE_LEDGER.md`.

## Where this chat is now

CERT-013 Windows lifecycle integration has completed all bounded live acceptance.

Accepted product/test code head:

`e11cf89ed26d551ca92b4010034d6e6792a9266b`

Reconcile CI #381:

- Linux full release checks PASS;
- Windows PowerShell 5.1 PASS.

Evidence/context/release-only commits after `e11cf89e...` do not alter the accepted CERT-013 product/test files.

## Live acceptance

### `SEC005 TEST`

Transactional Update — FULL PASS:

- worker returned `CERT_ROTATION=UNCHANGED`, setup returned `CERT-012_SETUP=PASS`;
- Update returned `UPDATE=PASS` + `CertificateRotation: managed`;
- identity/config/private+public SSH keys/known_hosts/Device ID/RDP port unchanged;
- main task Running, one Agent, one Hermes `ssh.exe`;
- rotation task Running as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM listener + TCP3389 unchanged;
- final `CERT-013_UPDATE=PASS`.

Repair lifecycle — FULL PASS:

- test removed only rotation Scheduled Task and `HermesRdpCertRotation.ps1`;
- public Repair returned core `REPAIR=PASS` plus `CertificateRotation: managed` and `CERT-013_REPAIR=PASS`;
- worker/task recreated automatically;
- identity/config/keys/known_hosts/RDP port unchanged;
- main Agent + one Hermes SSH process healthy;
- restored rotation task LocalSystem SID `S-1-5-18`;
- trusted CUSTOM binding unchanged, TCP3389 listening;
- final `CERT-013_REPAIR_LIVE=PASS`.

### Disposable clean fixture `DESKTOP-T9N368F`

Preflight PASS:

- Windows 10 Pro build 19045 x64;
- PowerShell 5.1 x64;
- Defender AV + real-time protection enabled;
- Hermes absent;
- OpenSSH Client Installed;
- final `CERT-013_CLEAN_FIXTURE=PASS`.

Fresh Install — FULL PASS from exact accepted head:

- `CERT_ROTATION=UPDATED`;
- `CERT-012_SETUP=PASS`;
- device `CERT013 FRESH`, endpoint `150.241.94.110:53394`;
- one main Agent + one Hermes SSH process;
- rotation task Running as LocalSystem SID `S-1-5-18`;
- trusted CUSTOM RDP thumbprint `2E170C609B47E0D34F16238503998509EDDDC79C`;
- TCP3389 listening;
- Defender enabled with no Hermes exclusion;
- final `CERT-013_FRESH_INSTALL=PASS`.

External Microsoft RDP — PASS:

- real connection to `150.241.94.110:53394` worked;
- trusted certificate worked with no warning.

Uninstall — FULL PASS:

- both Hermes Scheduled Tasks absent;
- Agent/rotation/SSH process counts zero;
- active `C:\ProgramData\HermesRDP` absent;
- validated archive `C:\ProgramData\HermesRDP.removed.20260814-132332`;
- Defender real-time protection remained enabled;
- final `CERT-013_UNINSTALL=PASS`.

## Exact resume action

PR #32 has no remaining live product gate.

1. Wait for CI on the final evidence-only PR head.
2. Mark PR #32 ready and merge with exact-head guard.
3. Delete disposable `CERT013 FRESH` in Telegram so token/key are revoked and port `53394` is freed.
4. Record merged SHA and continue to the next product gap.

Natural renewal-driven thumbprint rotation remains deferred until a real renewal. Do not force production issuance solely for evidence.

Never place private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
