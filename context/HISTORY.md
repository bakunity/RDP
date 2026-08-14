# Hermes RDP — History

## Milestones

### OpenSSH architecture stabilization

Hermes RDP moved to a dedicated reverse Microsoft OpenSSH transport with persistent per-device public endpoints, independent admin SSH, Telegram control and durable per-device identity.

Accepted product behavior includes external Microsoft RDP, multi-device operation/failure isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative compatibility, transactional updater rollback, existing-device Repair, Defender coexistence and the optimized main Agent fast path without the earlier RDP micro-freeze behavior.

### Trusted public-IP RDP certificate lifecycle — CERT-001 through CERT-012

A full trusted-certificate path was built and bounded live-accepted:

- Let’s Encrypt short-lived public-IP certificate issuance;
- Hermes-owned renewal scheduling;
- authenticated Windows certificate package delivery;
- non-exportable normal-API private-key behavior;
- `NETWORK SERVICE` key Read ACL;
- transactional CUSTOM RDP listener binding and correct rollback to Windows default self-signed state;
- external Microsoft RDP trust without the self-signed warning;
- non-secret certificate status/state;
- separate low-frequency LocalSystem rotation worker outside the main 3-second Agent loop;
- automatic recovery from controlled local listener drift;
- LocalSystem SID validation and global mutex ACL upgrade bug fixes.

PR #30 merged as `a03e406aaafeb5833bc720d3eef62cca60818118`.
PR #31 merged as `bd25db552aae8303356953fe2807a7bd855cba95`.

Natural renewal-driven new-thumbprint rotation remains a deferred real-world observation, not a blocker; do not force unnecessary production issuance.

### CERT-013 — normal Windows certificate lifecycle integration

CERT-013 integrated the accepted certificate rotation companion into ordinary Windows install/update/Repair/uninstall behavior so a normal user does not need a separate manual certificate setup command.

Accepted product/test code head before evidence-only commits:

`e11cf89ed26d551ca92b4010034d6e6792a9266b`

Reconcile CI #381 passed Linux full release checks and Windows PowerShell 5.1 validation.

Live acceptance completed on 2026-08-14:

- transactional Update on `SEC005 TEST`: FULL PASS while preserving identity/config/keys/known_hosts/device ID/RDP port/main runtime/trusted listener;
- targeted Repair on `SEC005 TEST`: FULL PASS after removing only rotation task/worker; lifecycle scaffolding was recreated without changing identity/port/tunnel/trusted binding;
- clean disposable fixture `DESKTOP-T9N368F`: Windows 10 Pro 19045 x64, PowerShell 5.1 x64, Defender enabled, Hermes absent before install;
- Fresh Install from accepted head: `CERT_ROTATION=UPDATED`, `CERT-012_SETUP=PASS`, main Agent + one Hermes SSH, LocalSystem rotation task SID `S-1-5-18`, trusted CUSTOM RDP listener, TCP3389, no Defender exclusion, final `CERT-013_FRESH_INSTALL=PASS`;
- real external Microsoft RDP to `150.241.94.110:53394`: connection and trusted certificate both PASS with no self-signed warning;
- normal Uninstall: both Hermes tasks absent, Agent/rotation/SSH counts zero, active client directory archived/removed, Defender still enabled, final `CERT-013_UNINSTALL=PASS`.

No CERT-013 live product gate remained after this acceptance. Later context/release-only commits do not change the accepted product/test code boundary.

## Historical deferred items

- SEC-004: fixture unavailable by design; do not reconstruct revoked credentials only to manufacture evidence.
- RL-006: PARTIAL only for an optional final exact-Windows one-process observation after already-clean reconnect cycles; do not repeat the stress test.
