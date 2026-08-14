# Hermes RDP — Unreleased

Base release: **v1.2.1**

Status: rolling engineering release ledger. Update continuously; do not wait until version-cut day.

## Merged / current main since v1.2.1

### Trusted public-IP RDP certificate lifecycle

A new trusted-certificate path was built so Microsoft Remote Desktop can validate the Windows RDP listener through a real public-IP certificate instead of the default Windows self-signed listener certificate.

Merged work includes:

- Hermes-owned Let’s Encrypt public-IP certificate setup and renewal scheduling;
- authenticated certificate package delivery to a registered Windows device;
- Windows import into LocalMachine with non-exportable private-key behavior through the normal API;
- `NETWORK SERVICE` private-key read ACL required by TermService;
- transactional RDP listener binding to CUSTOM certificate;
- correct rollback distinction between Windows default self-signed binding and explicit CUSTOM binding;
- automatic reapply of trusted certificate after local listener drift;
- non-secret server certificate state/status path;
- dedicated low-frequency Windows certificate-rotation worker outside the main 3-second Agent loop.

### Certificate lifecycle live acceptance

Bounded live acceptance proved:

- production public-IP certificate issuance and chain/key validation;
- Hermes renewal service/timer and non-secret state refresh;
- authenticated Windows PFX delivery/import;
- `NETWORK SERVICE` key access;
- CUSTOM RDP listener binding with TCP 3389 healthy;
- Microsoft Remote Desktop trust with no prior self-signed warning;
- explicit rollback to the exact original Windows default self-signed state;
- trusted reapply after rollback;
- automatic detection of deliberately-created self-signed drift;
- worker-triggered sync with `CERT_ROTATION=UPDATED` evidence;
- trusted CUSTOM listener automatically restored while RDP listener remained available.

### Rotation worker upgrade bugs found and resolved

Real Windows acceptance found two important integration issues:

- localized `SYSTEM` account names cannot be validated by literal English string comparison; validation now resolves the security principal to LocalSystem SID `S-1-5-18`;
- an existing SYSTEM worker could own `Global\HermesRdpCertificateRotation` with ACL that blocked administrator preflight during setup upgrade. Setup now stops the existing worker with bounded wait and the named mutex explicitly permits only LocalSystem + Builtin Administrators.

Both fixes passed Linux/Windows PowerShell 5.1 CI and live revalidation.

### CERT-013 — certificate rotation in ordinary Windows lifecycle

PR #32 merged as `c23c168a7719a31b4958a4eee555828858d0507c` after complete bounded live acceptance.

Normal Windows lifecycle now manages the trusted-certificate companion automatically:

- Fresh Install stages and validates Agent + certificate setup from one immutable SHA, brings up the OpenSSH runtime, then applies certificate lifecycle before reporting final success;
- transactional Update composes certificate setup before `UPDATE=PASS` while preserving outer rollback;
- Repair preserves the previously accepted core behavior and adds certificate lifecycle management with outer Agent/task snapshot rollback;
- Uninstall removes both main Agent and certificate-rotation runtime.

Live acceptance included:

- Update on `SEC005 TEST` with identity/config/SSH keys/known_hosts/Device ID/RDP port preserved;
- targeted Repair recreating deliberately removed rotation task/worker while preserving trusted RDP binding;
- clean Windows 10 Pro 19045 x64 / PowerShell 5.1 / Defender-enabled Fresh Install with automatic LocalSystem rotation task and no Defender exclusion;
- real external Microsoft Remote Desktop through `SERVER_IP_OR_DOMAIN:53394` with trusted certificate and no self-signed warning;
- normal Uninstall removing both tasks/processes and archiving/removing the active client directory while Defender stayed enabled.

Accepted product/test code head: `e11cf89ed26d551ca92b4010034d6e6792a9266b`; CI #381 PASS. Final evidence/privacy head `f868d8b554e4a6e1cb4a07d0625118696e946cda`; CI #410 PASS.

### Release-process hardening

Release documentation follows a durable source-of-truth model:

- compact public GitHub Release notes live in `docs/releases/vX.Y.Z.md`;
- long-form engineering history lives in `docs/releases/history/vX.Y.Z-full.md`;
- `UNRELEASED.md` accumulates work continuously;
- release workflow tags the validated workflow HEAD rather than the commit that last touched `VERSION`;
- existing GitHub Release descriptions synchronize from the corresponding versioned release-note file without rewriting historical tags.

## Deferred observation / not a blocker

### Natural certificate renewal rotation

The current short-lived production certificate should be allowed to renew naturally.

When the thumbprint changes naturally, capture only bounded evidence that:

- server state updates to the new thumbprint;
- Windows worker detects the new desired certificate;
- automatic rotation succeeds;
- a fresh Microsoft RDP connection remains trusted.

Do not force unnecessary production issuance solely to create this observation.

## Compatibility requirements carried forward

Do not regress:

- Windows PowerShell 5.1;
- Windows 10 x64 launched from x86/SysWOW64 PowerShell with Sysnative access to native OpenSSH;
- Windows Server support;
- Defender coexistence without exclusions/disablement;
- per-device Ed25519 identities;
- admin SSH isolation from Hermes tunnel sshd;
- transactional server/client update rollback;
- existing-device Repair identity boundary;
- main Agent fast path without certificate work in the 3-second loop.

## Known historical deferred items

- `RL-006` remains PARTIAL only for an optional final Windows one-process observation after already-clean reconnect cycles; do not repeat the stress test.
- `SEC-004` remains fixture-unavailable; do not reconstruct revoked credentials solely for artificial evidence.