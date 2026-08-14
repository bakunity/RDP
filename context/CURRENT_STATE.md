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
- Draft PR #30 is the active Windows certificate delivery/binding work.

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

## Live deployment truth

- Existing production controller/runtime remains unchanged until PR #30 is explicitly deployed.
- Server-side trusted public-IP issuance and renewal are live-proven.
- `SEC005 TEST` is the first non-critical Windows fixture for listener binding.

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
- bounded renewal service execution succeeds without renewing early;
- PR #29 productized setup reused the live production lineage without changing its serial;
- TCP 80 is free after lifecycle operations.

## CERT-010 Windows baseline — PASS

Read-only live inventory on `SEC005 TEST`:

- Windows 10 Pro 19045 x64;
- Windows PowerShell 5.1 x64;
- `TermService` Running / Automatic under NetworkService;
- `RDP-Tcp` TerminalServices CIM provider available;
- current RDP certificate is the default self-signed certificate (`hash type 1`), present in `LocalMachine\Remote Desktop` with private key and Server Authentication EKU;
- no explicit registry certificate hash binding exists;
- certificate import/CIM tools are present;
- RDP listener 3389 is listening on IPv4 and IPv6.

This provides a clean rollback baseline. No mutation occurred.

## PR #30 / CERT-011 implementation state

Draft PR #30 branch `feat/windows-rdp-cert-rotation`, tested head `af054274405c33849b8bbdee0a730320a8b5ab33`.

Implemented security model:

- existing per-device bearer token authenticates the certificate-package endpoint;
- API TLS remains fingerprint-pinned on Windows;
- privileged helper has no client-controlled path/command input and reads only the configured Hermes trusted lineage;
- exact sudoers command boundary, not broad root/filesystem access;
- PFX is generated ephemerally and not persisted server-side;
- Windows temporary PFX is ACL-restricted and deleted after import;
- LocalMachine import omits `-Exportable` and code verifies the resulting RSA key is non-exportable;
- NetworkService SID receives private-key Read;
- old listener thumbprint is captured before mutation;
- custom RDP binding and TCP 3389 are checked;
- local failure attempts immediate functional rollback to the old thumbprint.

CI #324: Linux full release checks PASS and Windows PowerShell 5.1 PASS.

No PR #30 server deploy has occurred yet and no Windows listener state has changed.

## Exact next step

Deploy immutable PR #30 head `af054274405c33849b8bbdee0a730320a8b5ab33` through `scripts/update-server.sh` on the current Linux certificate host. Verify transactional `UPDATE=PASS` before any Windows mutation.

After server deploy, run the immutable CERT-011 sync only on `SEC005 TEST`, then perform a real new Microsoft Remote Desktop connection and verify the intended certificate warning/name behavior. Periodic agent rotation is deferred until this bounded binding is live-accepted.
