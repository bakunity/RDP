# Hermes RDP — Current State Snapshot

Snapshot date: 2026-08-07

## Repository / release

- Repository: `bakunity/RDP`
- Product-code `main` at initial context creation: `6cecc33d520e8bd07c322d660c200a454d17e93f`; later commits include context documentation updates.
- Latest published GitHub Release at this snapshot: `v1.1.0`.
- `v1.1.0` is the OpenSSH transport release.
- Public site is deployed from this repository on Vercel.

Before changing code, always re-check current `main`, open branches/PRs and releases because this file is a snapshot, not a live repository query.

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

An expired short-lived pairing code caused one failed attempt, after which a fresh valid pairing flow succeeded. Treat this as a pairing UX/error-reporting issue, not a transport failure.

### Real external RDP

Confirmed successful RDP connection from a phone over mobile data. This is a real external-network end-to-end validation, not only a localhost/server port test.

### Windows reboot recovery

The user rebooted the tested Windows PC, waited for startup/reconnect and successfully connected over RDP again.

Evidence:

```text
Windows reboot -> Scheduled Task/agent/tunnel recover -> RDP usable again
PASS
```

This specific recovery scenario no longer belongs in the untested list unless later changes can regress it.

### Telegram OFF / ON user-visible behavior

The user tested control while an RDP session was active:

```text
OFF -> active RDP session disconnected / became unusable
ON  -> RDP session could connect again
```

The user explicitly confirmed that the ON/OFF functionality works.

Evidence classification:

- `OFF -> active RDP access interrupted`: **PASS**.
- `ON -> RDP access restored`: **PASS**.
- `OFF -> server endpoint independently measured CLOSED`: **NOT YET SEPARATELY PROVEN** in that final test.

Do not downgrade the real behavioral PASS merely because the telemetry UI is inaccurate, but do not overclaim a low-level listener measurement that was not made.

### Multi-device direction

The user reports that devices can be added and assigned ports work. A second endpoint from the normal pool has been observed in the Telegram dashboard. Formal isolation/revoke/delete acceptance for multiple devices remains to be completed.

## Open / not yet accepted

### Telegram state correctness

Current dashboard can report:

- agent ONLINE;
- `SSH tunnel: stopped`;
- endpoint/RDP actually usable.

This is internally inconsistent and must be fixed before the dashboard can be considered trustworthy.

The fact that real ON/OFF works does **not** close this bug. Control behavior and telemetry correctness are separate concerns.

### State semantics

The UI still does not clearly distinguish:

- PC/agent online state;
- access desired ON/OFF;
- pending/finished command;
- actual SSH process;
- server listener;
- RDP session.

Required state dimensions:

```text
Agent:        ONLINE | OFFLINE
Access:       ENABLED | DISABLED
Command:      IDLE | PENDING | SUCCESS | FAILED | TIMEOUT
SSH:          CONNECTED | DISCONNECTED | UNKNOWN
Endpoint:     OPEN | CLOSED | UNKNOWN
RDP sessions: N
```

### SSH telemetry detection

Likely issue: agent `Get-SshProcesses` is stricter than the installer runtime check and may fail to match the actual `ssh.exe` command line. Verify on the tested Windows machine before patching or declaring this the root cause.

Also rule out an orphan/legacy SSH process.

### Command lifecycle UX

Telegram currently communicates “command sent” more clearly than “command completed”. Dashboard v2 should use registry/command-result data to expose pending/success/failure/timeout.

### Server close helper

The close helper finds the PID owning the RDP listener and kills it if `/proc/<pid>/exe` resolves to `/usr/sbin/sshd`. Static tests exist. User-visible OFF behavior now passes, but a separate listener-level integration probe remains useful for proving exact endpoint state and DELETE cleanup.

### Legacy Windows ACL / reinstall

Current `main` installer must still be rechecked for the fragile recursive backup path over an existing protected Hermes directory. A real old installation previously produced access denied. Desired solution remains whole-directory archive/rename with scoped ACL fallback.

### Remaining recovery tests

Still need formal PASS for:

- temporary Windows network loss -> reconnect;
- Linux server reboot -> services + endpoints recover;
- controller restart;
- dedicated sshd restart;
- repeated reconnect without duplicate/orphan SSH processes.

Windows reboot recovery is already PASS and should not be listed here as untested.

### Remaining device-control acceptance

Still need formal PASS for:

- RESTART actually recreates/reconnects transport;
- DELETE revokes device API token and SSH key;
- DELETE closes endpoint;
- freed port reuse is safe;
- cross-port key isolation for multiple devices.

OFF/ON user-visible access behavior is already PASS. A separate low-level endpoint CLOSED/OPEN measurement can still be added to the acceptance matrix.

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

Core transport works. Fresh client installation works. External RDP works. Tested Windows reboot recovery works. Telegram OFF/ON works at the user-visible RDP level.

The next work is to make state truthful, command completion visible, remaining recovery deterministic, migrations/updates safe, and the product/documentation coherent.
