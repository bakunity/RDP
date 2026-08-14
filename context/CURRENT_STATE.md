# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed current evidence read `EVIDENCE_LEDGER.md`; v1.3.0 release evidence is archived separately.

## Repository / release

- Current stable published release: **v1.3.0**.
- Release PR #35 merged as `a51e942afbd17997a8100d554f8a0b2e50d4baa7`.
- Final pre-merge release candidate head `74834bd741b5b8794a4d0277976ea3650e35f6c2` passed CI #426 on Linux full release checks and Windows PowerShell 5.1.
- Annotated tag `v1.3.0` points to merge commit `a51e942afbd17997a8100d554f8a0b2e50d4baa7`.
- Release workflow run #30 succeeded; GitHub Release `Hermes RDP v1.3.0` is published and is the current latest release.

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

Certificate rotation is a separate low-frequency LocalSystem worker. It checks authenticated non-secret server certificate status and invokes full certificate sync only on thumbprint change or local listener drift. Certificate work stays outside the 3-second main Agent loop.

Admin SSH remains independent. FRP is not active runtime. Each Windows client keeps its own Ed25519 identity.

## v1.3.0 product boundary

The trusted RDP certificate lifecycle is an optional backward-compatible capability:

- server obtains/renews the public-IP certificate;
- authenticated Windows devices can retrieve the certificate package;
- Windows imports/binds a trusted CUSTOM RDP listener certificate;
- Fresh Install, Update and Repair manage the rotation companion automatically;
- Uninstall removes both main and rotation runtime;
- controlled local certificate drift recovers automatically.

Trusted mode requires a globally routable public IPv4 and reachable TCP 80 for ACME HTTP-01.

## Accepted compatibility baseline

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, transactional updater rollback, existing-device Repair, Defender coexistence, and CERT-001 through CERT-013.

Natural renewal-driven thumbprint rotation remains deferred until the real next renewal; do not force extra issuance for evidence.

SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture final one-process observation.

## Exact next step

Observe the next natural certificate renewal when it occurs, or explicitly choose the next product workstream. No v1.3.0 release work remains open.
