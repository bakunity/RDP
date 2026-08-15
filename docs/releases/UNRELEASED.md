# Unreleased

Detailed engineering ledger for changes after the current stable release.

## Added

- Zero-config interactive server bootstrap for the normal install path: one public command, secure Telegram bot-token prompt, private one-time owner claim, automatic public IPv4 discovery, and automatic trusted RDP certificate attempt.
- Server install preflight for Debian/Ubuntu APT health, including bounded repair of the known stale `archive.debian.org` Debian source case with a backup before mutation.

## Changed

- Public server installation UX now points normal users to `scripts/install.sh`; the existing `scripts/install-server.sh` remains the advanced/automation interface.
- Required server-side shell entrypoints are stored executable so GitHub source archives preserve the bootstrap execution contract.

## Fixed

- Telegram API bootstrap payload handling no longer corrupts an explicit `{}` JSON body through Bash parameter expansion.

## Validation

- Debian 13 Trixie live fixture with a stale `archive.debian.org` source: automatic APT repair PASS; backup created before mutation.
- Public IPv4 discovery: PASS.
- Telegram `getMe`, webhook-free validation, private one-time `/claim`, and owner binding: PASS.
- Exact immutable source archive resolution after executable-mode correction: PASS.
- Zero-config core server install: PASS; dedicated OpenSSH tunnel service and Hermes controller active; installer reached `=== HERMES RDP READY ===`.
- Existing nginx listener on TCP 80 correctly prevented the current standalone ACME path from taking over the port; core install remained healthy and reported trusted TLS unavailable instead of rolling back.
- Follow-up remaining before PR acceptance: nginx/webroot coexistence for automatic IP-certificate issuance and cleanup of duplicate APT source warnings produced by stale-source normalization.
