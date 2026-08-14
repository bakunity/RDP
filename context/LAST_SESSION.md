# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md` / `EVIDENCE_LEDGER.md`.

## Where this chat is now

Trusted public-IP RDP certificate work reached full bounded acceptance through CERT-012.

Merged work:

- PR #29 server certificate lifecycle;
- PR #30 authenticated Windows certificate delivery/binding + correct type-aware rollback;
- PR #31 automatic Windows certificate rotation, merge commit `bd25db552aae8303356953fe2807a7bd855cba95`.

Final PR #31 tested head: `14da128328589dfae6c8e3b6819977120be16739`; CI #353 Linux + Windows PowerShell 5.1 PASS.

## Key live proof

On non-critical `SEC005 TEST`:

- rotation task runs as LocalSystem SID `S-1-5-18`;
- unchanged state returns `CERT_ROTATION=UNCHANGED`;
- a global-mutex upgrade ACL bug was reproduced, rollback worked, then fixed and live accepted;
- controlled rollback to Windows default self-signed created real local drift;
- scheduled worker detected drift, invoked trusted sync itself and logged `CERT_ROTATION=UPDATED`;
- trusted CUSTOM listener returned, TCP 3389 stayed listening, worker stayed Running;
- fresh Microsoft Remote Desktop connection was protected/trusted with no self-signed warning.

Linux production has the accepted server-side certificate state/status/renewal slice deployed. Windows fixture has the final worker/setup fix.

Natural renewal-driven thumbprint rotation is deferred until the existing short-lived certificate renews normally. Do not force extra production issuance solely for evidence.

## Exact resume action

Start **CERT-013** from current `main`:

1. inspect normal Windows fresh install, transactional update, Repair and uninstall flows;
2. integrate the accepted rotation worker + sync companion transactionally so no separate manual setup command is needed;
3. preserve PowerShell 5.1, Win10 x86/Sysnative compatibility, LocalSystem SID validation, mutex ACL fix and rollback behavior;
4. keep certificate work out of the 3-second main agent loop;
5. add CI before any new live mutation.

Do not repeat CERT-001..CERT-012 acceptance without a concrete regression reason. Never put private keys, PFX passwords, API/device tokens, pairing codes or other secrets into context/chat.
