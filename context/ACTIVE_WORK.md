# Hermes RDP — Active Work

Updated: 2026-08-14

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.2.1**.
- PR #19–#29: merged / accepted stabilization and server certificate lifecycle work.
- PR #30 authenticated Windows trusted-certificate delivery/binding: **merged** as `a03e406aaafeb5833bc720d3eef62cca60818118` after full CERT-011 live acceptance.
- Active draft PR #31: `feat: automate trusted RDP certificate rotation`.
- PR #31 current immutable tested head: `79cab42d43e4d9cdca12b8a1380574f7d40460f6`.
- PR #31 CI #344: Linux full release checks PASS + Windows PowerShell 5.1 PASS.
- Linux production runtime is currently deployed on PR #31 head `79cab42d...` after CERT-012 server acceptance.

## Stable architecture

```text
Telegram control
      |
Hermes API/controller + SQLite
      |
dedicated Hermes sshd :7000
      |
reverse Microsoft OpenSSH
      |
Windows RDP :3389
      |
persistent endpoint per device
```

Admin SSH remains independent. FRP is not active runtime. Each Windows device has its own local Ed25519 identity.

## Accepted baseline — do not repeat without regression evidence

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell / Sysnative OpenSSH compatibility;
- Telegram OFF/ON/RESTART and status UX;
- Stage 3 security/device lifecycle;
- transactional Linux and Windows updater rollback;
- bounded Windows Repair success/rollback;
- Defender coexistence;
- trusted public-IP certificate CERT-001 through CERT-011.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted public-IP RDP certificate — accepted behavior

User decision: keep the current public-IP Let’s Encrypt certificate as-is; no domain or certificate cosmetic changes are needed.

CERT-011 is **fully live-accepted** on non-critical `SEC005 TEST`:

- authenticated PFX package delivery PASS;
- CNG private key imported non-exportable;
- `NETWORK SERVICE` Read ACL PASS;
- RDP listener changed to CUSTOM trusted thumbprint while TCP 3389 stayed listening;
- fresh Microsoft Remote Desktop connection reported server authenticity verified and used production Let’s Encrypt;
- explicit rollback restored the exact original Windows default self-signed state (`hash type 3 -> 1`) and the external warning returned;
- rollback bug root cause was confirmed and fixed: previous type `1` is restored by removing explicit custom registry binding, while previous type `3` restores the prior custom thumbprint;
- fixed reapply returned the trusted CUSTOM binding and a fresh external RDP connection was trusted again.

PR #30 merged after this bounded acceptance.

## CERT-012 — automatic certificate rotation — ACTIVE

Draft PR #31 deliberately keeps certificate work out of the performance-sensitive 3-second main agent loop.

Design:

- server publishes a root-owned non-secret certificate state (thumbprint/fingerprint/serial/expiry only);
- authenticated per-device `rdp-certificate-status` exposes only non-secret identity metadata;
- full PFX endpoint from PR #30 is called only when thumbprint changes or local RDP binding drifts;
- Windows uses a separate SYSTEM `Hermes RDP Certificate Rotation` worker with a default 15-minute cadence;
- worker uses pinned HTTPS + existing device token;
- unchanged trusted binding performs no PFX retrieval/import;
- drift/renewal reuses the accepted transactional `sync-rdp-certificate.ps1` path;
- global mutex prevents overlapping rotation workers.

### CERT-012 server live acceptance — PASS

Immutable deployed head: `79cab42d43e4d9cdca12b8a1380574f7d40460f6`.

Live evidence:

- transactional server updater `UPDATE=PASS`;
- production certificate serial unchanged;
- state refresher + renewal helpers installed;
- state file ownership/mode `root:hermes-rdp / 0640`;
- published thumbprint exactly matched the current certificate;
- state payload contained only expected non-secret fields;
- authenticated status endpoint installed;
- renewal service smoke PASS without forcing renewal;
- controller, dedicated sshd and renewal timer active;
- TCP 80 free after smoke.

## Exact resume action

Run the transactional PR #31 Windows rotation setup on `SEC005 TEST` using immutable head `79cab42d...`.

Expected first run with the currently correct trusted binding:

- `CERT_ROTATION=UNCHANGED`;
- `ROTATION_CHECK=PASS`;
- `ROTATION_TASK=RUNNING`;
- `CERT-012_SETUP=PASS`.

After that, create local RDP certificate drift using the already accepted default-self-signed rollback path, **do not manually reapply**, and require the rotation worker to restore the trusted CUSTOM binding automatically. Then confirm one fresh trusted external Microsoft RDP connection.

Do not expose PFX content/passwords, private keys, pairing codes, API tokens or other secret-bearing material in chat/context.
