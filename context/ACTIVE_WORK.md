# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #19–#25: merged / runtime accepted stabilization work.
- PR #26 documentation reconciliation: merged.
- PR #27 `v1.2.0`: historical packaging-error release; published tag is intentionally not rewritten.
- PR #28 `v1.2.1`: merged packaging hotfix; Linux + Windows PowerShell 5.1 CI PASS.
- PR #29 trusted public-IP certificate lifecycle: **merged** as `33c7b6ac6e5a6fb732963988c4734a8a7ef8ec5e` after immutable live acceptance.
- Production controller/app still runs the previously accepted runtime until the active CERT-011 branch is explicitly deployed.

## Secondary release follow-up

Prepared branch `fix/release-tag-head-v2` remains at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`; no PR is open. This remains secondary to the certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: do not add a domain only for appearance. The trusted identity is the existing public IPv4. The Microsoft Remote Desktop warning is controlled by the certificate presented by the **Windows RDP listener**, not Linux/API TLS.

### CERT-001 through CERT-009 — PASS

Already accepted and must not be repeated without regression evidence:

- Debian 13 certificate-host inventory;
- Certbot 5.7.0 under `/opt/certbot` with `/usr/local/bin/certbot` entry point;
- public TCP 80 / HTTP-01 reachability through UFW;
- Let’s Encrypt staging public-IP issuance using standalone HTTP-01 + `shortlived` + RSA 2048;
- staging key/fullchain inspection and renewal dry-run;
- production Let’s Encrypt public-IP issuance, IP SAN, Server Authentication EKU, certificate/key match and local trust validation;
- scheduler-gap inventory;
- Hermes-owned renewal service/timer live acceptance;
- PR #29 productized server lifecycle immutable live acceptance with existing production lineage reuse, unchanged serial, timer active/enabled, `PASS_NOT_DUE`, TCP 80 free and rollback backup.

### CERT-010 — Windows listener read-only inventory — PASS

Live inventory on non-critical `SEC005 TEST` proved:

- Windows 10 Pro build 19045, 64-bit OS;
- Windows PowerShell 5.1 running as a 64-bit process;
- `TermService` Running / Automatic under `NT AUTHORITY\NetworkService`;
- `Win32_TSGeneralSetting` for `RDP-Tcp` is available;
- current listener uses the Windows default self-signed certificate (`SSLCertificateSHA1HashType=1`);
- current self-signed certificate exists in `LocalMachine\Remote Desktop`, has a private key and Server Authentication EKU;
- no explicit registry `SSLCertificateSHA1Hash` binding is set;
- `Import-PfxCertificate`, `Get-PfxCertificate` and `Set-CimInstance` are available;
- TCP 3389 listens on IPv4 and IPv6.

No Windows listener mutation occurred during CERT-010.

### CERT-011 — authenticated Windows certificate delivery/binding — ACTIVE

Draft PR **#30**: `feat: add authenticated Windows RDP certificate rotation`.

Branch: `feat/windows-rdp-cert-rotation`.
Tested head: `af054274405c33849b8bbdee0a730320a8b5ab33`.

Implemented:

- per-device authenticated `POST /v1/devices/{id}/rdp-certificate` endpoint;
- existing device bearer auth is checked before any privileged helper invocation;
- root-owned bounded helper reads only the configured trusted Hermes lineage and generates an ephemeral password-protected PFX;
- controller does not receive direct filesystem read permission to `/etc/letsencrypt`;
- exact-command sudoers rule permits only `/usr/local/sbin/hermes-rdp-cert-package`;
- Windows `sync-rdp-certificate.ps1` uses existing pinned HTTPS + device token;
- PFX import targets `LocalMachine\My` without `-Exportable`, then verifies the RSA key is non-exportable;
- `NETWORK SERVICE` receives Read on the private-key file using SID `S-1-5-20`;
- previous RDP thumbprint is saved before mutation;
- custom `SSLCertificateSHA1Hash` binding is verified locally together with TCP 3389;
- local failures trigger functional rollback to the previous thumbprint;
- setup/update/uninstall manage the helper and sudoers rule transactionally;
- update rollback includes helper/sudoers restoration/removal.

CI #324 on PR #30 head `af054274...`: **Linux full release checks PASS + Windows PowerShell 5.1 PASS**.

No PR #30 code is deployed yet. No Windows certificate has been imported or bound yet.

## Security boundary

The short-lived public-IP private key remains shared per Hermes server because separate public certificates for every Windows device using the same IP do not scale well. The shared key must therefore never be exposed by a static/public URL or broad filesystem permission.

Current design sends an ephemeral password-protected PFX only after existing device authentication over the already pinned HTTPS channel. The PFX is temporary on Windows and the imported private key is required to be non-exportable.

## Exact resume action

Deploy immutable PR #30 head `af054274405c33849b8bbdee0a730320a8b5ab33` to the current Linux certificate host with the transactional server updater. Confirm `UPDATE=PASS`, services healthy, helper/sudoers installed and certificate lineage unchanged.

Then run **CERT-011** only on `SEC005 TEST` using the immutable Windows sync script. Acceptance requires package auth, non-exportable import, NETWORK SERVICE Read ACL, CUSTOM listener hash, TCP 3389 still listening, and a real Microsoft Remote Desktop reconnect/trust check.

Only after CERT-011 live acceptance integrate periodic rotation into the normal Hermes Windows agent.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
