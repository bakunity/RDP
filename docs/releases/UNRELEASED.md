# Unreleased

Detailed engineering ledger for changes after the current stable release.

## Added

- Zero-config interactive server bootstrap for the normal install path: one public command, secure Telegram bot-token prompt, private one-time owner claim, automatic public IPv4 discovery, and automatic trusted RDP certificate attempt.
- Server install preflight for Debian/Ubuntu APT health, including bounded repair of the known stale `archive.debian.org` Debian source case with a backup before mutation.
- Automatic nginx/webroot ACME coexistence for public-IP certificates when nginx already owns TCP 80; free TCP 80 keeps the standalone path.

## Changed

- Public server installation UX now points normal users to `scripts/install.sh`; the existing `scripts/install-server.sh` remains the advanced/automation interface.
- Required server-side shell entrypoints are stored executable so GitHub source archives preserve the bootstrap execution contract.
- Trusted certificate setup now refuses non-nginx TCP 80 conflicts, validates a dedicated IP-only nginx challenge route before ACME, and preserves the existing nginx service without stop/restart.
- Hermes-managed nginx ACME configuration is backed up with server uninstall evidence and removed/reloaded on normal uninstall while certificate lineage remains preserved.

## Fixed

- Telegram API bootstrap payload handling no longer corrupts an explicit `{}` JSON body through Bash parameter expansion.
- Trusted RDP certificate setup no longer treats an existing nginx listener on TCP 80 as an automatic failure.

## Validation

- Debian 13 Trixie live fixture with a stale `archive.debian.org` source: automatic APT repair PASS; backup created before mutation.
- Public IPv4 discovery: PASS.
- Telegram `getMe`, webhook-free validation, private one-time `/claim`, and owner binding: PASS.
- Exact immutable source archive resolution after executable-mode correction: PASS.
- Zero-config core server install: PASS; dedicated OpenSSH tunnel service and Hermes controller active; installer reached `=== HERMES RDP READY ===`.
- Existing nginx listener on TCP 80 was confirmed active with valid configuration and standard `conf.d/*.conf` plus `sites-enabled/*` includes.
- nginx/webroot coexistence implementation: CI #441 Linux full release checks PASS and Windows PowerShell 5.1 PASS.
- Remaining live gate before PR acceptance: run only the trusted-certificate setup against the installed fixture and confirm `acme_mode=nginx-webroot`, `tcp80=NGINX_WEBROOT`, `TRUSTED_RDP_CERT=PASS`, nginx remains active, and the existing site remains unaffected.
- Duplicate APT source warnings observed after the provider image repair remain a non-blocking installer-cleanup follow-up; they did not affect core installation.
