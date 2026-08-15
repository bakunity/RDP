# Unreleased

Detailed engineering ledger for changes after the current stable release.

## Added

- Zero-config interactive server bootstrap for the normal install path: one public command, secure Telegram bot-token prompt, private one-time owner claim, automatic public IPv4 discovery, and automatic trusted RDP certificate attempt.
- Server install preflight for Debian/Ubuntu APT health, including bounded repair of the known stale `archive.debian.org` Debian source case with a backup before mutation.
- Automatic nginx/webroot ACME coexistence for public-IP certificates when nginx already owns TCP 80; free TCP 80 keeps the standalone path.
- Bounded nginx readiness probing after reload so ACME validation waits for the new challenge route instead of racing old workers.

## Changed

- Public server installation UX now points normal users to `scripts/install.sh`; the existing `scripts/install-server.sh` remains the advanced/automation interface.
- Telegram bot-token entry is masked with `*`; empty or invalid input is retried up to three times without printing the token.
- Required server-side shell entrypoints are stored executable so GitHub source archives preserve the bootstrap execution contract.
- Trusted certificate setup now refuses non-nginx TCP 80 conflicts, validates a dedicated IP-only nginx challenge route before ACME, and preserves the existing nginx service without stop/restart.
- nginx ACME challenge files use a dedicated readable webroot under `/var/www/hermes-rdp-acme` and a direct `alias` mapping rather than the previously failing `root + try_files` combination.
- Hermes-managed nginx ACME configuration is backed up with server uninstall evidence and removed/reloaded on normal uninstall while certificate lineage remains preserved.
- APT preflight cleanup now merges overlapping simple `deb`/`deb-src` entries with the same type + URI + suite by preserving the union/order of components; backup, post-mutation `apt-get update` validation and rollback remain mandatory.

## Fixed

- Telegram API bootstrap payload handling no longer corrupts an explicit `{}` JSON body through Bash parameter expansion.
- Empty or mistyped Telegram bot-token input no longer terminates the normal install immediately.
- GitHub source archive resolution no longer fails because required server scripts lack executable mode.
- Trusted RDP certificate setup no longer treats an existing nginx listener on TCP 80 as an automatic failure.
- nginx ACME setup no longer uses a private Hermes state path that is unsuitable for the nginx worker.
- nginx ACME route no longer returns a false 404 from the old `root + try_files` mapping.
- nginx reload no longer races the first ACME route probe; readiness is bounded and retried.
- APT duplicate-target warnings caused by overlapping component sets are normalized safely instead of requiring byte-identical source lines.

## Validation

- Debian 13 Trixie live fixture with a stale `archive.debian.org` source: automatic APT repair PASS; backup created before mutation.
- First live duplicate-target cleanup attempt failed safely and rolled back; diagnosis confirmed overlapping component sets rather than exact duplicate lines.
- Bounded semantic APT component-union cleanup then allowed the clean-reinstall flow to proceed; the subsequent exact-head install reported clean APT repositories.
- Public IPv4 discovery: PASS.
- Telegram `getMe`, webhook-free validation, private one-time `/claim`, owner binding and normal `/start` dashboard: PASS.
- Masked Telegram token display: live PASS. Empty/invalid retry behavior is regression-tested; no token is printed or stored in evidence.
- Exact immutable source archive resolution after executable-mode correction: PASS.
- A full Hermes state purge followed by a fresh install from exact head `056bf7473ff851157f4c749f233fb0fb8b57a133`: PASS; dedicated OpenSSH tunnel service and controller active; installer reached `=== HERMES RDP READY ===`.
- An intentional terminal interruption during the owner-claim phase left no partially installed Hermes core; rerunning the normal installer from that clean state succeeded.
- Existing nginx listener on TCP 80 remained active with its pre-existing site configuration intact.
- nginx routing and direct ACME `alias` mapping: live probe PASS (`HTTP 200` for both route and challenge file).
- Let's Encrypt staging and production short-lived public-IP issuance through nginx webroot were previously accepted live; the clean reinstall reused the preserved valid lineage and re-established the Hermes lifecycle without forced reissuance.
- Fresh-install trusted-certificate lifecycle: `renewal_timer=active`, `renewal_enabled=enabled`, `renewal_smoke=PASS_NOT_DUE`, `acme_mode=nginx-webroot`, `tcp80=NGINX_WEBROOT`, `package_helper=READY`, `certificate_state=READY`, `TRUSTED_RDP_CERT=PASS`.
- Exact code boundary `056bf7473ff851157f4c749f233fb0fb8b57a133`: CI #459 Linux full release checks PASS and Windows PowerShell 5.1 PASS.
- The temporary clean-reinstall fixture helper used only for bounded acceptance is removed before PR readiness.
