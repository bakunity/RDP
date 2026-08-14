# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` historical packaging-error release; tag is not rewritten.
- PR #28: `v1.2.1` packaging hotfix merged and remains stable.
- PR #29 trusted public-IP server certificate lifecycle is merged as `33c7b6ac6e5a6fb732963988c4734a8a7ef8ec5e`.
- Draft PR #30 is the active Windows certificate delivery/binding work; exact head `af054274405c33849b8bbdee0a730320a8b5ab33` is deployed for bounded acceptance.

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

Admin SSH remains independent from Hermes tunnel SSH. FRP is not active runtime. Each Windows client keeps its own local Ed25519 identity.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason:

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell/Sysnative;
- Telegram OFF/ON/RESTART and automatic dashboard refresh;
- Stage 3 security/device lifecycle acceptance;
- transactional server/Windows updater rollback acceptance;
- existing-device Repair acceptance;
- Microsoft Defender real-time protection coexistence.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its deferred exact-Windows one-process observation.

## Trusted certificate state

Server-side certificate lifecycle is accepted:

- Certbot 5.7.0 under `/opt/certbot`;
- public HTTP-01 reachability through UFW/TCP 80;
- staging and production public-IP issuance;
- production IP SAN, Server Authentication EKU, RSA 2048, certificate/key match and local trust verification;
- Hermes-owned renewal service/timer enabled and active;
- PR #29 productized setup reused the live production lineage without changing its serial;
- TCP 80 is free after lifecycle operations.

## CERT-010 Windows baseline — PASS

Read-only live inventory on `SEC005 TEST` established Windows 10 Pro 19045 x64 / PowerShell 5.1 x64, default self-signed RDP certificate, TerminalServices CIM availability, rollback thumbprint, certificate tools and listening TCP 3389.

## CERT-011 — core live acceptance PASS

Draft PR #30 branch `feat/windows-rdp-cert-rotation`, tested/deployed head `af054274405c33849b8bbdee0a730320a8b5ab33`.

CI #324: Linux full release checks PASS and Windows PowerShell 5.1 PASS.

Live server deploy:

- transactional updater `UPDATE=PASS`;
- certificate serial unchanged;
- helper/sudoers installed and runtime helper execution through `hermes-rdp -> sudo` PASS;
- controller, dedicated sshd and renewal timer active;
- TCP 80 free.

Live Windows binding on `SEC005 TEST`:

- authenticated package retrieval PASS;
- PFX import PASS;
- private key provider CNG;
- imported private key verified non-exportable;
- NetworkService Read ACL PASS;
- RDP listener moved from saved self-signed thumbprint to the trusted certificate;
- hash type CUSTOM;
- TCP 3389 still listening;
- rollback metadata preserved.

External Microsoft Remote Desktop acceptance:

- a fresh connection through the normal Hermes public-IP endpoint succeeded;
- client showed **“Подлинность удаленного компьютера проверена с помощью сертификата сервера”** rather than the old untrusted-certificate warning;
- certificate UI showed production Let’s Encrypt issuer `YR1` and the expected short-lived validity window.

The trusted public-IP RDP goal is therefore live-proven. PR #30 remains draft only until the explicit rollback/reapply path is bounded-live-accepted.

## Exact next step

On `SEC005 TEST`, invoke the immutable sync script with `-Rollback`, verify the saved old thumbprint is restored and RDP remains functional, then run normal sync again to restore the trusted CUSTOM binding and perform one fresh trusted RDP reconnect. After that PR #30 can become merge-ready; periodic renewal-driven agent rotation remains the next product step.
