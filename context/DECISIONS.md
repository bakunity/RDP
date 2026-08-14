# Hermes RDP — Decisions

## Architecture

- Use dedicated Hermes OpenSSH reverse tunnels for Windows RDP transport.
- Keep admin SSH independent from Hermes tunnel sshd.
- Keep one Ed25519 identity per Windows device.
- Keep certificate lifecycle work outside the performance-sensitive main Agent loop.

## Windows compatibility

- Windows PowerShell 5.1 is a supported product boundary.
- Win10 x64 launched from x86/SysWOW64 PowerShell must reach native OpenSSH/PowerShell through Sysnative where required.
- Do not require users to upgrade PowerShell for Hermes.
- Defender must remain enabled; Hermes must not depend on broad Defender exclusions.

## Trusted RDP certificate lifecycle

- Certificate identity is the public Hermes IP; no cosmetic domain is required for the Windows RDP listener trust goal.
- Use the Windows RDP listener certificate, not Linux/API HTTPS certificate presentation, to eliminate the Microsoft Remote Desktop self-signed warning.
- Use a separate low-frequency LocalSystem certificate rotation worker rather than adding certificate work to the main 3-second Agent loop.
- Server status checks expose only non-secret desired certificate state; PFX delivery occurs only through authenticated sync when required.
- Validate LocalSystem by SID `S-1-5-18`, not localized account display name.
- Global rotation mutex ACL is limited to LocalSystem and Builtin Administrators.
- Do not overclaim non-exportable Windows private keys as protection against a fully compromised/admin endpoint.

## CERT-013 lifecycle composition

Accepted 2026-08-14:

- normal fresh install, transactional Update and Repair all manage certificate rotation automatically from the same immutable repository SHA;
- accepted pre-CERT-013 Repair logic is preserved byte-for-byte as `repair-client-core.ps1`, with the public Repair wrapper composing certificate lifecycle and outer main Agent/task rollback;
- uninstall removes both main and certificate-rotation tasks/processes before archiving/removing the active Hermes client directory;
- x86 PowerShell -> native/Sysnative compatibility remains part of these lifecycle flows;
- CERT-013 accepted product/test code head is `e11cf89ed26d551ca92b4010034d6e6792a9266b` with CI #381 Linux + Windows PowerShell 5.1 PASS;
- bounded live acceptance covers Update, Repair, clean Fresh Install, real external trusted RDP and Uninstall; do not repeat without regression evidence.

## Release process

- `docs/releases/UNRELEASED.md` is the rolling engineering ledger for the next release.
- Public GitHub Release notes stay compact in `docs/releases/vX.Y.Z.md`.
- Full engineering history belongs in `docs/releases/history/vX.Y.Z-full.md`.
- Release workflow tags the exact validated workflow HEAD, not the commit that last touched `VERSION`.
- Historical release descriptions may be synchronized from versioned release-note files without rewriting historical tags.

## Deferred evidence

- Allow short-lived production certificate renewal to occur naturally; do not force issuance solely to manufacture a new-thumbprint observation.
- SEC-004 remains fixture-unavailable by design.
- RL-006 remains PARTIAL only for its optional final exact-Windows one-process observation; do not repeat the already-clean stress cycles.

## Secrets

Never store private SSH keys, pairing codes, API/device tokens, PFX passwords or equivalent secrets in repository context/release notes/chat.
