# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #29 trusted public-IP server certificate lifecycle: merged/live accepted.
- PR #30 authenticated Windows certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after complete CERT-011 acceptance.
- PR #31 automatic certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after bounded CERT-012 acceptance.
- PR #32 CERT-013 lifecycle integration: **draft/open**, head `29c19182ef99497b4cc314e3b4e9b6598ad95516`; CI #363 Linux + Windows PowerShell 5.1 PASS.
- CERT-013 transactional Update and Repair lifecycle are live accepted on `SEC005 TEST`; fresh install/uninstall remain pending on a disposable fixture only.

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

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, Stage 3 security/device lifecycle, transactional updater rollback, existing-device Repair, Defender coexistence, CERT-001 through CERT-012, and CERT-013 Update/Repair live acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted certificate state

The server has one production short-lived Let’s Encrypt public-IP lineage with Hermes-owned renewal scheduling. `SEC005 TEST` presents the trusted CUSTOM certificate and Microsoft Remote Desktop connects without the previous self-signed warning.

Natural renewal-driven thumbprint rotation remains deferred to the real next renewal; do not force extra production issuance for evidence.

## CERT-013 current boundary

PR #32 integrates the accepted rotation companion into normal Windows lifecycle flows.

Live accepted on `SEC005 TEST`:

- **Update FULL PASS:** ordinary transactional Update automatically managed certificate rotation from the same immutable SHA; device/config/key/known_hosts/port identity stayed unchanged; main Agent/tunnel and rotation task remained healthy; trusted RDP binding/3389 unchanged.
- **Repair FULL PASS:** only rotation task + worker were removed; public Repair recreated them automatically while preserving identity, port, tunnel, trusted CUSTOM listener and TCP 3389. Final `CERT-013_REPAIR_LIVE=PASS`.

`SEC005 TEST` must not be used for destructive fresh-install/uninstall acceptance.

## Exact next step

Use a separate disposable supported Windows PC/VM for the final CERT-013 gate:

1. fresh install from exact PR #32 head;
2. verify tunnel + automatic rotation companion + trusted RDP;
3. run normal uninstall and verify both Hermes tasks/processes are removed;
4. if PASS, update evidence/context, mark PR #32 ready and merge with exact-head guard.

If no disposable fixture exists, leave PR #32 draft instead of risking the accepted `SEC005 TEST` machine.
