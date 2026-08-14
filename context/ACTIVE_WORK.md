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

### CERT-011 — authenticated Windows certificate delivery/binding — PARTIAL PASS

Draft PR **#30**: `feat: add authenticated Windows RDP certificate rotation`.

Branch: `feat/windows-rdp-cert-rotation`.
Tested/deployed head: `af054274405c33849b8bbdee0a730320a8b5ab33`.
CI #324: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

Implemented:

- per-device authenticated `POST /v1/devices/{id}/rdp-certificate` endpoint;
- existing bearer auth is checked before privileged helper invocation;
- bounded root helper reads only the configured trusted Hermes lineage and emits an ephemeral password-protected PFX;
- controller has no direct read access to `/etc/letsencrypt`;
- exact-command sudoers rule permits only the package helper;
- Windows sync uses existing pinned HTTPS + device token;
- PFX imports to `LocalMachine\My` without `-Exportable` and verifies private-key non-exportability;
- `NETWORK SERVICE` Read is applied to the private-key file;
- previous listener thumbprint is saved before mutation;
- custom RDP binding and local TCP 3389 are verified;
- local failures trigger functional rollback;
- server setup/updater/uninstall manage helper/sudoers transactionally.

Live server acceptance on PR #30 head:

- transactional updater returned `UPDATE=PASS`;
- Let’s Encrypt certificate serial remained unchanged;
- package helper files/sudoers present;
- helper executed successfully through the real `hermes-rdp -> sudo` path without exposing PFX/password in chat;
- controller, dedicated sshd and renewal timer remained active;
- TCP 80 remained free.

Live Windows local-binding acceptance on non-critical `SEC005 TEST`:

- authenticated certificate package retrieval: PASS;
- PFX import: PASS;
- private-key provider: CNG;
- private key verified non-exportable;
- `NETWORK SERVICE` Read ACL: PASS;
- RDP listener changed from the saved default self-signed thumbprint to the trusted certificate thumbprint;
- `SSLCertificateSHA1HashType` became CUSTOM;
- TCP 3389 remained listening;
- rollback file exists at the Hermes data path.

CERT-011 is not fully complete yet because the external client acceptance has not been performed. No claim yet that the Microsoft Remote Desktop certificate warning is gone.

## Security boundary

The short-lived public-IP private key remains shared per Hermes server because separate public certificates for every Windows device using the same IP do not scale well. The shared key must never be exposed by a static/public URL or broad filesystem permission.

Current design sends an ephemeral password-protected PFX only after existing device authentication over the pinned HTTPS channel. The temporary PFX is deleted after use, and the imported Windows private key is required to be non-exportable.

## Exact resume action

Complete the **external CERT-011 acceptance**:

1. from a separate Microsoft Remote Desktop client, open a **new** connection to the normal Hermes public endpoint for `SEC005 TEST` using the public IP address;
2. confirm the connection succeeds and the previous certificate identity/trust warning is absent;
3. if a warning remains, capture only its exact text/screenshot and do not delete the rollback state;
4. after external PASS, test the explicit Hermes rollback path once, then reapply trusted binding and confirm reconnect again;
5. only after those bounded checks integrate periodic certificate sync into the normal Windows agent and validate a real renewal-driven rotation cycle.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
