# Hermes RDP — Project Handoff

Updated: 2026-08-14

## Current product state

Hermes RDP uses a dedicated OpenSSH reverse-tunnel architecture:

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

Admin SSH is independent. FRP is not active runtime. Each Windows device has its own Ed25519 identity.

Trusted RDP certificate work is separate from the performance-sensitive main Agent loop. A low-frequency LocalSystem rotation worker checks non-secret desired certificate state and invokes authenticated PFX sync only on thumbprint change or local listener drift.

## Stable release

Current published stable release: **v1.2.1**.

Release-note process is durable:

- `docs/releases/UNRELEASED.md` accumulates work continuously;
- compact public release notes live in `docs/releases/vX.Y.Z.md`;
- full engineering history lives in `docs/releases/history/vX.Y.Z-full.md`;
- release workflow tags the validated workflow HEAD and synchronizes release bodies without rewriting historical tags.

## Accepted baseline — do not repeat without regression evidence

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation/failure isolation;
- Windows and Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell -> Sysnative/native OpenSSH compatibility;
- Telegram OFF/ON/RESTART + status UX;
- Stage 3 security/device lifecycle;
- transactional server/client update rollback;
- existing-device Repair success/rollback;
- Defender coexistence;
- CERT-001 through CERT-012 trusted public-IP certificate lifecycle;
- CERT-013 normal Windows lifecycle integration: Update, Repair, clean Fresh Install, external trusted RDP, Uninstall.

SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional deferred exact-Windows one-process observation.

## CERT-013 final accepted boundary

PR #32 accepted product/test code head:

`e11cf89ed26d551ca92b4010034d6e6792a9266b`

Reconcile CI #381:

- Linux full release checks PASS;
- Windows PowerShell 5.1 PASS.

Live acceptance:

- `SEC005 TEST`: transactional Update FULL PASS and targeted Repair FULL PASS while preserving identity/config/keys/known_hosts/device ID/RDP port/tunnel/trusted listener.
- disposable `DESKTOP-T9N368F`: clean Win10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled preflight PASS.
- Fresh Install from exact accepted head: `CERT_ROTATION=UPDATED`, `CERT-012_SETUP=PASS`, one Agent, one Hermes SSH, LocalSystem rotation task SID `S-1-5-18`, trusted CUSTOM listener, TCP3389, no Defender exclusion, final `CERT-013_FRESH_INSTALL=PASS`.
- external Microsoft RDP to `150.241.94.110:53394`: connection PASS, trusted certificate/no self-signed warning.
- normal Uninstall: both tasks absent, Agent/rotation/SSH counts zero, active base directory archived/removed, Defender remained enabled, final `CERT-013_UNINSTALL=PASS`.

Evidence/context/release-only commits after `e11cf89e...` do not alter the accepted CERT-013 product/test code.

## Immediate resume point

1. Require green CI on the final evidence-only PR #32 head.
2. Mark PR #32 ready and merge with exact-head guard.
3. Delete disposable `CERT013 FRESH` device in Telegram so token/key are revoked and RDP port `53394` is freed.
4. Record merged PR #32 SHA in context.
5. Continue with the next product gap; do not reopen completed CERT-013 tests without regression evidence.

## Deferred observation

Allow the current short-lived production certificate to renew naturally. When it does, capture only bounded old/new thumbprint, server-state refresh, automatic Windows rotation and fresh trusted Microsoft RDP evidence. Do not force production issuance solely for testing.

## Secrets rule

Never store pairing codes, API/device tokens, SSH private keys, PFX passwords or other secrets in context/release notes/chat.
