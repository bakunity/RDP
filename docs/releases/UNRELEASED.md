# Unreleased

Detailed engineering ledger for changes after the current stable release.

## Added

- Zero-config interactive server bootstrap for the normal install path: one public command, secure Telegram bot-token prompt, private one-time owner claim, automatic public IPv4 discovery, and automatic trusted RDP certificate attempt.
- Server install preflight for Debian/Ubuntu APT health, including bounded repair of the known stale `archive.debian.org` Debian source case with a backup before mutation.
- Automatic nginx/webroot ACME coexistence for public-IP certificates when nginx already owns TCP 80; free TCP 80 keeps the standalone path.
- Bounded nginx readiness probing after reload so ACME validation waits for the new challenge route instead of racing old workers.

## Changed

- Public server installation UX now points normal users to `scripts/install.sh`; the existing `scripts/install-server.sh` remains the advanced/automation interface.
- Required server-side shell entrypoints are stored executable so GitHub source archives preserve the bootstrap execution contract.
- Trusted certificate setup now refuses non-nginx TCP 80 conflicts, validates a dedicated IP-only nginx challenge route before ACME, and preserves the existing nginx service without stop/restart.
- nginx ACME challenge files use a dedicated readable webroot under `/var/www/hermes-rdp-acme` and a direct `alias` mapping rather than the previously failing `root + try_files` combination.
- Hermes-managed nginx ACME configuration is backed up with server uninstall evidence and removed/reloaded on normal uninstall while certificate lineage remains preserved.
- APT preflight cleanup remains transactional: backup before mutation, `apt-get update` validation after mutation, and rollback on failure.

## Fixed

- Telegram API bootstrap payload handling no longer corrupts an explicit `{}` JSON body through Bash parameter expansion.
- GitHub source archive resolution no longer fails because required server scripts lack executable mode.
- Trusted RDP certificate setup no longer treats an existing nginx listener on TCP 80 as an automatic failure.
- nginx ACME setup no longer uses a private Hermes state path that is unsuitable for the nginx worker.
- nginx ACME route no longer returns a false 404 from the old `root + try_files` mapping.
- nginx reload no longer races the first ACME route probe; readiness is bounded and retried.

## Validation

- Debian 13 Trixie live fixture with a stale `archive.debian.org` source: automatic APT repair PASS; backup created before mutation.
- Public IPv4 discovery: PASS.
- Telegram `getMe`, webhook-free validation, private one-time `/claim`, owner binding and normal `/start` dashboard: PASS.
- Exact immutable source archive resolution after executable-mode correction: PASS.
- Zero-config core server install: PASS; dedicated OpenSSH tunnel service and Hermes controller active; installer reached `=== HERMES RDP READY ===`.
- Existing nginx listener on TCP 80 remained active with its pre-existing site configuration intact.
- nginx routing and direct ACME `alias` mapping: live probe PASS (`HTTP 200` for both route and challenge file).
- Let's Encrypt staging short-lived public-IP certificate issuance through nginx webroot: PASS.
- Let's Encrypt production short-lived public-IP certificate issuance through nginx webroot: PASS.
- Hermes trusted-certificate lifecycle: `renewal_timer=active`, `renewal_enabled=enabled`, `renewal_smoke=PASS_NOT_DUE`, `acme_mode=nginx-webroot`, `tcp80=NGINX_WEBROOT`, `package_helper=READY`, `certificate_state=READY`, `TRUSTED_RDP_CERT=PASS`.
- Exact code boundary `0aa6bed193abcd6ef60673304695e7565d697011`: CI #453 Linux full release checks PASS and Windows PowerShell 5.1 PASS. Evidence/context checkpoint CI #454 also PASS.
- First live APT cleanup attempt failed safely and rolled back. Root cause is confirmed: two entries for the same `deb URI suite` overlap in components (`main contrib` versus `main contrib non-free non-free-firmware`), so APT reports duplicate targets although the source lines are not byte-identical.
- Remaining acceptance: replace exact-line cleanup with bounded semantic component-union normalization, then perform one clean-room Hermes uninstall/reinstall on the fixture and run final CI before PR readiness.
