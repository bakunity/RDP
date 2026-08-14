# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md` / `EVIDENCE_LEDGER.md`.

## Where this chat is now

CERT-013 normal Windows lifecycle integration is complete and merged.

- accepted product/test code head: `e11cf89ed26d551ca92b4010034d6e6792a9266b`;
- reconcile CI #381: Linux full release checks PASS + Windows PowerShell 5.1 PASS;
- final evidence/privacy head: `f868d8b554e4a6e1cb4a07d0625118696e946cda`;
- final CI #410: PASS;
- PR #32 merged as `c23c168a7719a31b4958a4eee555828858d0507c`.

## Live acceptance completed

### `SEC005 TEST`

- Transactional Update: FULL PASS, final `CERT-013_UPDATE=PASS`.
- Targeted Repair after removing only certificate-rotation task/worker: FULL PASS, final `CERT-013_REPAIR_LIVE=PASS`.
- Identity/config/private+public SSH keys/known_hosts/Device ID/RDP port stayed unchanged.
- Main Agent/tunnel and trusted CUSTOM RDP listener remained healthy.

### Disposable fixture `DESKTOP-T9N368F`

- clean Win10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled preflight: `CERT-013_CLEAN_FIXTURE=PASS`;
- Fresh Install from accepted head: automatic certificate lifecycle, one Agent + one Hermes SSH, LocalSystem rotation task SID `S-1-5-18`, trusted CUSTOM listener, no Defender exclusion, final `CERT-013_FRESH_INSTALL=PASS`;
- real external Microsoft RDP through `SERVER_IP_OR_DOMAIN:53394`: connection worked, trusted certificate/no self-signed warning;
- normal Uninstall: both tasks absent, Agent/rotation/SSH counts zero, active client directory archived/removed, Defender remained enabled, final `CERT-013_UNINSTALL=PASS`.

## Exact resume action

1. Delete disposable `CERT013 FRESH` device in Telegram so its token/key are revoked and port `53394` is freed.
2. Reconcile README/docs/website with the now-merged automatic trusted-certificate lifecycle.
3. Decide the next patch/minor release boundary from `docs/releases/UNRELEASED.md`; do not publish automatically.

Natural renewal-driven certificate rotation remains deferred/non-blocking. Do not force production issuance solely for evidence.

Do not repeat CERT-013 live tests without a concrete regression reason. Never place private keys, PFX passwords, API/device tokens or pairing codes into context/chat.