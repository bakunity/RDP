# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #19–#25: merged / runtime accepted stabilization work.
- PR #26 documentation reconciliation: merged.
- PR #27 `v1.2.0`: historical packaging-error release; published tag is intentionally not rewritten.
- PR #28 `v1.2.1`: merged packaging hotfix; Linux + Windows PowerShell 5.1 CI PASS.
- Production controller/app still runs accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`; certificate work has not redeployed the controller/runtime.

## Secondary release follow-up

Prepared branch `fix/release-tag-head-v2` remains at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`; no PR is open. This remains secondary to the certificate track.

## Current product track — trusted RDP certificate on public IP

User decision: do not add a domain only for appearance. The trusted identity is the existing public IPv4. The Microsoft Remote Desktop warning is controlled by the certificate presented by the **Windows RDP listener**, not Linux/API TLS.

### CERT-001 through CERT-006 — PASS

Already accepted and must not be repeated without regression evidence:

- Debian 13 certificate-host inventory;
- Certbot 5.7.0 under `/opt/certbot` with `/usr/local/bin/certbot` entry point;
- public TCP 80 / HTTP-01 reachability through UFW;
- Let’s Encrypt staging public-IP issuance using standalone HTTP-01 + `shortlived` + RSA 2048;
- staging certificate/key/fullchain inspection and `certbot renew --dry-run`;
- production Let’s Encrypt public-IP issuance;
- production IP SAN, TLS Server Authentication EKU, certificate/private-key match and local trust-chain verification.

### CERT-007 — scheduler inventory — PASS / GAP CONFIRMED

Live inventory proved the pip/venv Certbot installation had no systemd timer/service and no cron entry running `certbot renew`.

### CERT-008 — Hermes-owned automatic renewal — PASS

- `hermes-rdp-cert-renew.service` and `.timer` created;
- `systemd-analyze verify` PASS;
- timer enabled/active;
- twice-daily schedule with `RandomizedDelaySec=1h` and `Persistent=yes`;
- bounded manual service run returned success and did not renew early;
- TCP `80` remained free.

### CERT-009 — productized server lifecycle live acceptance — PASS

Draft PR #29 branch `feat/trusted-rdp-cert-lifecycle`, tested immutable head `e914a0f45a6cc734d25b02340353fc06ace6c7c8`.

Repository implementation includes:

- `scripts/setup-trusted-rdp-cert.sh` for Certbot install, isolated staging validation, production issuance/reuse, certificate/key validation, UFW 80 and timer setup;
- repository-owned renewal wrapper with `flock`;
- repository-owned renewal service/timer matching accepted runtime cadence;
- `install-server.sh --trusted-rdp-cert` explicit opt-in; default install unchanged;
- uninstall removes Hermes-owned renewal units/wrapper while preserving ACME lineage/private material;
- release gates enforce lifecycle invariants.

CI:

- CI #313: Linux PASS + Windows PowerShell 5.1 PASS;
- CI #316 after installer/uninstall wiring: Linux PASS + Windows PowerShell 5.1 PASS.

Live acceptance on the current certificate host:

- immutable PR #29 module detected and reused the existing production lineage;
- certificate serial before/after remained identical (`CERTIFICATE_REUSED=PASS`);
- no new certificate request was made;
- Hermes config records trusted certificate enabled, correct cert name, `shortlived` profile and renewal timer;
- repository-owned renewal timer remained enabled/active;
- renewal smoke returned `PASS_NOT_DUE`;
- TCP `80` remained free;
- journal showed clean renewal service start/finish;
- rollback backup was created before adoption.

No Windows RDP listener certificate state has been changed yet.

## Certificate architecture constraint

Per-device public certificates with separate Windows-local private keys are attractive for isolation, but all Hermes devices behind one server are reached through the same public IP and Let’s Encrypt limits new certificates for the exact same identifier set. Issuing one independent public-IP certificate per device does not scale as the default product model.

Current product direction: one short-lived public-IP lineage per Hermes server plus a strongly authenticated Windows distribution/rotation path. Do not expose the shared private key through an unauthenticated or weak endpoint.

## Exact resume action

PR #29 has satisfied its server-side merge gate: CI PASS + immutable live acceptance PASS. Merge/reconcile PR #29, then start **CERT-010** as a separate Windows certificate distribution/binding track.

CERT-010 design constraints already confirmed from current Hermes source:

- devices authenticate to the API with a long random bearer token; only SHA-256 of the token is stored server-side;
- the Windows agent already uses TLS certificate fingerprint pinning for API calls;
- `device.json`, the SSH private key and `known_hosts` are ACL-restricted to SYSTEM and Administrators;
- Windows certificate delivery must reuse this authenticated pinned channel, avoid public/static secret URLs, import into `LocalMachine\My` with a non-exportable private key, grant RDP's service identity read access, capture the current listener thumbprint before mutation, and provide deterministic rollback.

First Windows mutation remains the non-critical `SEC005 TEST` fixture only.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.
