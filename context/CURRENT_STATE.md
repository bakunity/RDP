# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #29 trusted public-IP server certificate lifecycle: merged/live accepted.
- PR #30 authenticated Windows certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after complete CERT-011 live acceptance.
- Draft PR #31 automatic certificate rotation is active at immutable head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`.
- CI #344 on that head: Linux PASS + Windows PowerShell 5.1 PASS.
- Linux runtime is currently deployed on the PR #31 head after CERT-012 server acceptance.

## Runtime architecture

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

Admin SSH remains independent. FRP is not active runtime. Each Windows client keeps its own local Ed25519 identity.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, Stage 3 security/device lifecycle, transactional updater rollback, Repair, Defender coexistence, and trusted-certificate CERT-001 through CERT-011.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted certificate state

The server has one production short-lived Let’s Encrypt public-IP lineage with Hermes-owned renewal scheduling. The Windows RDP listener on `SEC005 TEST` is currently back on the trusted CUSTOM certificate after the accepted rollback/reapply sequence. A fresh external Microsoft Remote Desktop connection is trusted without the prior self-signed warning.

User chose to keep the certificate representation as-is; no domain/CN cosmetic work is pending.

## CERT-011 — COMPLETE PASS

On `SEC005 TEST`:

- authenticated package retrieval PASS;
- PFX imported with CNG non-exportable private key;
- `NETWORK SERVICE` Read ACL PASS;
- CUSTOM listener binding PASS with TCP 3389 continuously listening;
- fresh external Microsoft RDP trusted the production Let’s Encrypt certificate;
- corrected rollback restored exact Windows default self-signed hash type `1` and the expected external warning;
- fixed reapply restored the trusted CUSTOM binding and trusted external behavior.

Confirmed rollback root cause: Windows default self-signed state has no explicit custom registry binding; type `1` must be restored by removing that binding, not by assigning the self-signed thumbprint as CUSTOM.

## CERT-012 — server side PASS / Windows worker pending

PR #31 implements automatic rotation outside the main 3-second agent loop.

Live server acceptance on immutable head `79cab42d...`:

- `UPDATE=PASS`;
- certificate serial unchanged;
- non-secret certificate state helpers installed;
- state file `root:hermes-rdp` mode `0640`;
- state thumbprint matched current production certificate;
- state payload contained only expected non-secret metadata;
- authenticated status endpoint installed;
- renewal smoke PASS;
- controller/sshd/renewal timer active;
- TCP 80 free.

## Exact next step

Install the PR #31 rotation worker transactionally on `SEC005 TEST` from immutable head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`.

The first preflight must report `CERT_ROTATION=UNCHANGED` because local CUSTOM binding already matches server state, then create/start the SYSTEM task `Hermes RDP Certificate Rotation` and report `CERT-012_SETUP=PASS`.

After that, use the already accepted rollback mechanism to create local self-signed drift and let the worker restore trusted binding automatically without manual reapply.
