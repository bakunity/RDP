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
- Production controller/app is currently deployed on PR #30 initial accepted server head `af054274405c33849b8bbdee0a730320a8b5ab33`; the newer rollback fix changes only the Windows sync/test layer.

## Secondary release follow-up

Prepared branch `fix/release-tag-head-v2` remains at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`; no PR is open. This remains secondary to the certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: do not add a domain only for appearance. The trusted identity is the existing public IPv4. The Microsoft Remote Desktop warning is controlled by the certificate presented by the **Windows RDP listener**, not Linux/API TLS.

### CERT-001 through CERT-010 — PASS

Already accepted and must not be repeated without regression evidence:

- Debian 13 certificate-host inventory;
- Certbot 5.7.0 under `/opt/certbot`;
- public TCP 80 / HTTP-01 reachability;
- staging and production Let’s Encrypt public-IP issuance with `shortlived` + RSA 2048;
- key/fullchain/renewal validation;
- production IP SAN, Server Authentication EKU, key match and local trust validation;
- scheduler-gap inventory and Hermes-owned renewal timer/service acceptance;
- PR #29 productized server lifecycle immutable live acceptance and merge;
- CERT-010 Windows 10 Pro x64 / PowerShell 5.1 x64 RDP listener inventory on `SEC005 TEST`, including default self-signed baseline and rollback thumbprint.

### CERT-011 — authenticated Windows certificate delivery/binding — CORE PASS, reapply gate active

Draft PR **#30**: `feat: add authenticated Windows RDP certificate rotation`.
Branch: `feat/windows-rdp-cert-rotation`.
Current head: `83e1b0b5d89b2728646a8eb518026ba9d1cf575a`.

Initial implementation CI #324 on `af054274...`: Linux PASS + Windows PowerShell 5.1 PASS.
Rollback-fix CI #333 on `83e1b0b...`: Linux PASS + Windows PowerShell 5.1 PASS.

Live server acceptance on the initial PR #30 head:

- transactional updater `UPDATE=PASS`;
- Let’s Encrypt certificate serial unchanged;
- package helper files/sudoers present;
- helper executed through the real `hermes-rdp -> sudo` path;
- controller, dedicated sshd and renewal timer remained active;
- TCP 80 remained free.

Live Windows trusted binding on `SEC005 TEST`:

- authenticated package retrieval PASS;
- PFX import PASS;
- CNG private key verified non-exportable;
- `NETWORK SERVICE` Read ACL PASS;
- listener changed from default self-signed to trusted CUSTOM thumbprint;
- TCP 3389 remained listening;
- rollback metadata preserved.

External Microsoft Remote Desktop trusted acceptance:

- a fresh Hermes RDP connection succeeded;
- the client reported that remote-computer authenticity was verified with the server certificate rather than showing the prior untrusted warning;
- certificate UI showed production Let’s Encrypt issuer `YR1` and the expected short-lived validity window.

Therefore the core trusted public-IP RDP objective is live PASS.

### CERT-011 rollback bug — RESOLVED / LIVE-ACCEPTED

The first explicit rollback attempt failed with `Set-CimInstance` / `HRESULT 0x80041008` because the original Windows default self-signed listener was hash type `1` with no explicit registry `SSLCertificateSHA1Hash`. Restoring that state as a CUSTOM binding is invalid.

Correct rollback behavior was live-proven on Windows 10:

- remove the explicit custom registry binding;
- hash type returns `3 -> 1`;
- exact original self-signed thumbprint returns;
- TCP 3389 remains listening;
- a fresh external Microsoft Remote Desktop connection succeeds again and the expected self-signed/untrusted certificate warning returns.

PR #30 head `83e1b0b...` implements type-aware rollback in both explicit and automatic failure paths:

- previous type `1`: remove explicit custom binding and verify Windows default self-signed state returns;
- previous type `3`: restore the previous custom thumbprint through CIM;
- other hash types are rejected rather than guessed.

CI #333 validates the rollback fix on Linux and Windows PowerShell 5.1.

## Exact resume action

`SEC005 TEST` is intentionally in the restored Windows default self-signed state after the fully accepted rollback.

1. Reapply trusted binding using PR #30 fixed head `83e1b0b5d89b2728646a8eb518026ba9d1cf575a`.
2. Confirm local CUSTOM binding / TCP 3389 and one fresh external trusted RDP connection again.
3. Then PR #30 can become merge-ready and merge.
4. After merge, integrate periodic certificate sync into the normal Hermes Windows agent and live-test a real renewal-driven rotation cycle.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
