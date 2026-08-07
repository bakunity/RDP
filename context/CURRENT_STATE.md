# Hermes RDP — Current State Snapshot

Snapshot date: 2026-08-07

## Repository / release

- Repository: `bakunity/RDP`
- Main at snapshot creation: `6cecc33d520e8bd07c322d660c200a454d17e93f` before context commits were added.
- Latest published GitHub Release: `v1.1.0`.
- `v1.1.0` is the OpenSSH transport release.
- Public site is deployed from this repository on Vercel.

## Confirmed PASS

### Server/OpenSSH architecture

- dedicated `hermes-rdp-sshd.service` exists;
- controller/API service exists;
- system administrative SSH remains separate;
- FRP is not part of the current OpenSSH runtime architecture;
- device authorization is based on individual SSH public keys;
- `permitlisten` limits each key to its assigned endpoint;
- API uses HTTPS pinning;
- SSH host key is pinned through the trusted API path.

### Windows installation

A clean OpenSSH-based Windows install has completed successfully with:

- built-in Windows OpenSSH;
- Ed25519 key generation;
- device registration;
- permanent RDP port allocation;
- Scheduled Task `Hermes RDP Agent`;
- working reverse forwarding.

### Real external RDP

Confirmed successful RDP connection from a phone over mobile data. This is a real external-network end-to-end validation, not only a localhost/server port test.

### Multi-device direction

The user reports that devices can be added and assigned ports work. A second endpoint from the normal pool has been observed in the Telegram dashboard. Formal isolation/recovery/delete acceptance for multiple devices remains to be completed.

## Open / not yet accepted

### Telegram state correctness

Current dashboard can report:

- agent ONLINE;
- `SSH tunnel: stopped`;
- endpoint available;
- active RDP connection.

This is internally inconsistent and must be fixed before the dashboard can be considered trustworthy.

### ON/OFF semantics

Current buttons send commands but do not make the state transition understandable. The UI does not clearly distinguish:

- PC/agent online state;
- access desired ON/OFF;
- pending command;
- actual SSH process;
- server listener;
- RDP session.

An OFF command must be validated by the actual endpoint becoming closed, not by a Telegram callback saying the command was sent.

### SSH telemetry detection

Likely issue: agent `Get-SshProcesses` is stricter than the installer runtime check and may fail to match the actual `ssh.exe` command line. Verify on a test Windows machine before patching.

### Server close helper

The close helper finds the PID owning the RDP listener and kills it if `/proc/<pid>/exe` resolves to `/usr/sbin/sshd`. This has static tests but still needs real reverse-forward integration validation for OFF/DELETE behavior.

### Legacy Windows ACL / reinstall

Current `main` installer still uses recursive backup of the existing Hermes directory. A real old installation containing a protected key previously produced an access-denied failure. The desired move-whole-directory fix is not confirmed merged.

### Recovery tests

Still need formal PASS for:

- Windows reboot;
- Linux server reboot;
- temporary network loss;
- controller restart;
- reconnect timing.

### Device-control acceptance

Still need formal PASS for:

- OFF closes endpoint;
- ON reopens endpoint;
- RESTART replaces/reconnects transport;
- DELETE revokes device access;
- DELETE closes listener;
- freed port reuse.

### Update / rollback

Current updater behavior is not yet a complete transactional production contract. Need runtime health checks and automatic rollback on failed deployment/client update.

## Documentation status

Documentation is not currently considered final.

Known issues:

- current architecture documentation is less explanatory than `v1.0.7`;
- some files still contain stale FRP concepts;
- README lost useful visual badges/buttons and architectural emphasis from the older version;
- release state wording became stale after `v1.1.0` was actually published;
- docs need a full consistency sweep after behavior is stabilized.

## Website status

The site is deployed and technically functional, but the user does not accept the current design/copy as final.

Treat current site as an interim version. Do not spend time polishing it before control/state correctness and reliability are fixed. Plan a real Website v2 redesign afterward.

## Definition of current phase

The project is in **stabilization**, not feature discovery.

Core transport works. The next work is to make state truthful, commands deterministic, recovery reliable, upgrades safe, and the product/documentation coherent.