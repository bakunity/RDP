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

The production certificate lineage is valid and no Windows RDP listener binding has been changed yet.

### CERT-007 — scheduler inventory — PASS / GAP CONFIRMED

Live read-only inventory proved that the pip/venv Certbot installation had no systemd timer/service and no cron entry running `certbot renew`.

### CERT-008 — Hermes-owned automatic renewal — PASS

Live runtime acceptance completed:

- `hermes-rdp-cert-renew.service` and `.timer` created;
- `systemd-analyze verify` PASS;
- timer is `enabled` and `active`;
- schedule is twice daily with `RandomizedDelaySec=1h` and `Persistent=yes`;
- bounded manual service run returned `Result=success`, exit status `0`;
- certificate was correctly not renewed early;
- TCP `80` was free after service execution;
- journal recorded clean start/finish.

### CERT-009 — productization in Hermes RDP — ACTIVE

Draft PR **#29**: `feat: add trusted RDP certificate lifecycle module`.

Branch: `feat/trusted-rdp-cert-lifecycle`.
Current head: `e914a0f45a6cc734d25b02340353fc06ace6c7c8`.

Implemented in the PR:

- `scripts/setup-trusted-rdp-cert.sh` encapsulates Certbot install, isolated staging validation, production issuance/reuse, certificate/key validation, UFW 80 and timer setup;
- Hermes renewal wrapper uses `flock` and certificate-specific normal `certbot renew`;
- repository-owned renewal service/timer match the accepted runtime cadence;
- `install-server.sh` exposes explicit opt-in `--trusted-rdp-cert`; default install behavior is unchanged;
- installer requires a globally routable IPv4 for this option;
- uninstall removes Hermes-owned renewal units/wrapper but deliberately preserves the ACME lineage/private material;
- release checks enforce staging, `shortlived`, IP issuance, locking, timer persistence/randomization, installer wiring and non-destructive uninstall behavior.

CI evidence:

- CI #313 on the lifecycle module: Linux PASS + Windows PowerShell 5.1 PASS.
- CI #316 after installer/uninstall wiring: Linux full release checks PASS + Windows PowerShell 5.1 PASS.

No PR #29 code has been deployed to production yet. No Windows certificate delivery/binding has been implemented yet.

## Certificate architecture constraint

Per-device public certificates with separate Windows-local private keys are attractive for isolation, but Let’s Encrypt limits new certificates for the exact same identifier set. Because all Hermes devices behind one server are reached through the same public IP, issuing one independent public-IP certificate per device does not scale as the default product model.

Current product direction for the next stage: one short-lived public-IP lineage per Hermes server, then a carefully authenticated/rotated Windows distribution path. Do not expose the shared private key through a weak or unauthenticated endpoint.

## Exact resume action

Complete **CERT-009 live acceptance** on the current certificate host using the immutable PR #29 head. The setup module must detect and reuse the already-valid production lineage rather than request another certificate, install the repository-owned wrapper/units, add the trusted-certificate config marker, and pass its bounded renewal smoke test without changing the certificate serial or leaving TCP `80` occupied.

After CERT-009 live acceptance:

1. checkpoint the runtime evidence and reconcile PR #29;
2. design/implement the authenticated Windows certificate delivery + rotation path;
3. preserve the existing Windows RDP listener certificate/state as rollback;
4. first bind/test only on non-critical `SEC005 TEST`;
5. validate the actual Microsoft Remote Desktop trust/name warning before expansion.

Do not expose private keys, pairing codes, API tokens or secret-bearing certificate material in chat/context.
