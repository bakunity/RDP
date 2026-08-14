# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md` / `EVIDENCE_LEDGER.md`.

## Where this chat is now

Hermes RDP **v1.3.0 is published and is the current stable/latest release**.

- final release candidate head: `74834bd741b5b8794a4d0277976ea3650e35f6c2`;
- exact-head CI #426: Linux full release checks PASS + Windows PowerShell 5.1 PASS;
- PR #35 merged as `a51e942afbd17997a8100d554f8a0b2e50d4baa7`;
- release workflow run #30: PASS;
- annotated tag `v1.3.0` points exactly to the merge commit;
- GitHub Release `Hermes RDP v1.3.0` is published and `releases/latest` resolves to it.

## Released product boundary

v1.3.0 includes the accepted trusted public-IP RDP certificate lifecycle and its integration into normal Windows Fresh Install, Update, Repair and Uninstall. Automatic local certificate drift recovery is accepted. Win10 x64/x86 PowerShell/Sysnative, Windows Server 2019 and Defender coexistence remain compatibility requirements.

Detailed release evidence was frozen to `context/archive/releases/v1.3.0-evidence.md` and the default evidence ledger was compacted for the new cycle.

## Exact resume action

No v1.3.0 release work remains.

When the short-lived production certificate renews naturally, collect only bounded non-secret evidence that server state refreshes, Windows rotates automatically and fresh Microsoft RDP remains trusted. Do not force extra production issuance solely for evidence.

If development continues before that event, explicitly select the next product workstream and create a new branch from current `main`; do not reopen accepted v1.3.0 runtime tests without regression evidence.

RL-006 remains optional/partial on the original exact fixture. SEC-004 remains fixture-unavailable.

Never place private keys, PFX passwords, API/device tokens or pairing codes into context/chat.
