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
- Production controller/app is currently deployed on PR #30 immutable head `af054274405c33849b8bbdee0a730320a8b5ab33` for bounded CERT-011 acceptance.

## Secondary release follow-up

Prepared branch `fix/release-tag-head-v2` remains at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`; no PR is open. This remains secondary to the certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: do not add a domain only for appearance. The trusted identity is the existing public IPv4. The Microsoft Remote Desktop warning is controlled by the certificate presented by the **Windows RDP listener**, not Linux/API TLS.

### CERT-001 through CERT-010 — PASS

Already accepted and must not be repeated without regression evidence:

- Debian 13 certificate-host inventory;
- Certbot 5.7.0 under `/opt/certbot` with `/usr/local/bin/certbot` entry point;
- public TCP 80 / HTTP-01 reachability through UFW;
- Let’s Encrypt staging public-IP issuance using standalone HTTP-01 + `shortlived` + RSA 2048;
- staging key/fullchain inspection and renewal dry-run;
- production Let’s Encrypt public-IP issuance, IP SAN, Server Authentication EKU, certificate/key match and local trust validation;
- scheduler-gap inventory;
- Hermes-owned renewal service/timer live acceptance;
- PR #29 productized server lifecycle immutable live acceptance and merge;
- CERT-010 read-only Windows 10 Pro x64 / PowerShell 5.1 x64 RDP listener inventory on `SEC005 TEST`, proving default self-signed baseline, TerminalServices CIM availability, rollback thumbprint, certificate tools and TCP 3389 listener.

### CERT-011 — authenticated Windows certificate delivery/binding — CORE PASS, rollback/reapply pending

Draft PR **#30**: `feat: add authenticated Windows RDP certificate rotation`.

Branch: `feat/windows-rdp-cert-rotation`.
Tested/deployed head: `af054274405c33849b8bbdee0a730320a8b5ab33`.
CI #324: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

Implemented and live-accepted so far:

- authenticated per-device certificate package endpoint;
- bearer auth before privileged helper execution;
- bounded root helper reading only the configured trusted Hermes lineage;
- exact-command sudoers boundary;
- pinned HTTPS delivery to Windows;
- PFX import into `LocalMachine\My` without `-Exportable`;
- imported CNG private key verified non-exportable;
- `NETWORK SERVICE` Read ACL on the private key;
- previous RDP thumbprint saved before mutation;
- custom RDP listener binding verified with TCP 3389 still listening;
- transactional server updater deployed exact PR #30 head with `UPDATE=PASS`;
- Let’s Encrypt certificate serial stayed unchanged during server deploy;
- package helper runtime path `hermes-rdp -> sudo` passed;
- controller, dedicated sshd and renewal timer remained active; TCP 80 remained free.

External Microsoft Remote Desktop acceptance on `SEC005 TEST`:

- fresh connection through the normal Hermes public-IP endpoint succeeded;
- Microsoft Remote Desktop displayed **“Подлинность удаленного компьютера проверена с помощью сертификата сервера”** instead of the prior untrusted-certificate warning;
- certificate dialog showed production Let’s Encrypt issuer `YR1` and the expected short-lived validity window.

Therefore the core CERT-011 objective — a publicly trusted certificate actually presented by the Windows RDP listener through Hermes — is **PASS**.

## Security boundary

The short-lived public-IP private key remains shared per Hermes server because separate public certificates for every Windows device using the same IP do not scale well. The shared key must never be exposed by a static/public URL or broad filesystem permission.

Current design sends an ephemeral password-protected PFX only after existing device authentication over the pinned HTTPS channel. The temporary PFX is deleted after use, and the imported Windows private key is required to be non-exportable.

## Exact resume action

Complete the **CERT-011 rollback/reapply acceptance** on `SEC005 TEST` before merging PR #30:

1. invoke the immutable sync script with `-Rollback` and verify the saved previous thumbprint is restored and TCP 3389 remains functional;
2. re-run normal sync and verify the trusted certificate is re-applied as CUSTOM with the same trusted thumbprint;
3. perform one fresh RDP connection after reapply to confirm trusted behavior still holds;
4. only then mark PR #30 merge-ready.

After PR #30 bounded acceptance, integrate periodic certificate sync into the normal Hermes Windows agent so renewal-driven rotation becomes automatic, then live-test one real renewal/rotation cycle before expanding to other Windows devices.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
