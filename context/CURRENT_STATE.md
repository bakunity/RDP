# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #29 trusted public-IP server certificate lifecycle: merged/live accepted.
- PR #30 authenticated Windows certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after complete CERT-011 acceptance.
- PR #31 automatic certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after bounded CERT-012 acceptance.
- PR #32 CERT-013 lifecycle integration has completed all bounded live acceptance. Product/test code acceptance head: `e11cf89ed26d551ca92b4010034d6e6792a9266b`; reconcile CI #381 Linux + Windows PowerShell 5.1 PASS.
- Evidence-only context/release commits after `e11cf89e...` do not modify CERT-013 product/test code.

## Runtime architecture

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

Certificate rotation is a separate low-frequency LocalSystem worker. It checks authenticated non-secret server certificate status and only invokes full PFX sync on thumbprint change/local listener drift. Certificate work stays outside the 3-second main Agent loop.

Admin SSH remains independent. FRP is not active runtime. Each Windows client keeps its own Ed25519 identity.

## Accepted baseline

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, Stage 3 security/device lifecycle, transactional updater rollback, existing-device Repair, Defender coexistence, CERT-001 through CERT-012, and full CERT-013 lifecycle acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted certificate state

The server has one production short-lived Let’s Encrypt public-IP lineage with Hermes-owned renewal scheduling. Accepted Windows fixtures present the trusted CUSTOM certificate and Microsoft Remote Desktop connects without the previous self-signed warning.

Natural renewal-driven thumbprint rotation remains deferred to the real next renewal; do not force extra production issuance for evidence.

## CERT-013 accepted boundary

PR #32 integrates the accepted rotation companion into normal Windows lifecycle flows.

Live accepted:

- **Update FULL PASS (`SEC005 TEST`)**: ordinary transactional Update automatically manages certificate rotation from the same immutable SHA; device/config/key/known_hosts/port identity stayed unchanged; main Agent/tunnel and rotation task remained healthy; trusted RDP binding/3389 unchanged.
- **Repair FULL PASS (`SEC005 TEST`)**: only rotation task + worker were removed; public Repair recreated them automatically while preserving identity, port, tunnel, trusted CUSTOM listener and TCP 3389.
- **Fresh Install FULL PASS (`DESKTOP-T9N368F`)**: clean Windows 10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled fixture installed from accepted head `e11cf89e...`; main Agent + SSH tunnel + LocalSystem rotation task came up automatically; trusted CUSTOM listener bound; no Defender exclusion required.
- **External RDP PASS**: real connection to `150.241.94.110:53394` worked with trusted certificate and no self-signed warning.
- **Uninstall FULL PASS**: both Hermes tasks and all Hermes Agent/rotation/SSH processes removed; active client directory archived/removed; Defender real-time protection remained enabled.

## Exact next step

1. Wait for final evidence-only PR head CI to be green.
2. Mark PR #32 ready and merge with exact-head guard.
3. Delete disposable `CERT013 FRESH` registration in Telegram to revoke its token/key and free port `53394`.
4. Record merged PR #32 SHA in context and continue to the next product gap.
