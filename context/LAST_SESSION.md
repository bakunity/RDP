# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md` / `EVIDENCE_LEDGER.md`.

## Where this chat is now

CERT-013 Windows lifecycle integration is active in draft PR #32.

Current exact tested head:

`29c19182ef99497b4cc314e3b4e9b6598ad95516`

CI #363:

- Linux full release checks PASS;
- Windows PowerShell 5.1 PASS.

## Live acceptance on `SEC005 TEST`

Transactional Update — FULL PASS:

- ordinary Update automatically ran certificate lifecycle setup from the same immutable SHA;
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

The earlier acceptance-wrapper function name `H` collided with Windows PowerShell `Get-History` before product mutation. Corrected wrapper passed; this was not a Hermes runtime bug.

## Exact resume action

Do not use `SEC005 TEST` for destructive fresh-install/uninstall acceptance.

Final PR #32 merge gate requires a separate disposable supported Windows test fixture:

1. fresh install from exact head `29c19182...`;
2. verify pairing/OpenSSH tunnel, automatic certificate companion, LocalSystem task, trusted CUSTOM listener, TCP3389 and external RDP;
3. run normal uninstall;
4. verify both Hermes tasks/processes removed and active client directory archived according to current uninstall behavior;
5. if PASS, update evidence/context, mark PR #32 ready and merge with exact-head guard.

If no disposable fixture exists, leave PR #32 draft instead of risking `SEC005 TEST`.

Natural renewal-driven thumbprint rotation remains deferred until a real renewal. Do not force production issuance solely for evidence.

Never place private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
