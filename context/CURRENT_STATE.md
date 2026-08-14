# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #29 trusted public-IP server certificate lifecycle: merged/live accepted.
- PR #30 authenticated Windows certificate delivery/binding: merged as `a03e406aaafeb5833bc720d3eef62cca60818118` after complete CERT-011 live acceptance.
- PR #31 automatic certificate rotation: merged as `bd25db552aae8303356953fe2807a7bd855cba95` after complete bounded CERT-012 live acceptance.
- Final PR #31 tested head `14da128328589dfae6c8e3b6819977120be16739`; CI #353 Linux PASS + Windows PowerShell 5.1 PASS.
- Linux runtime remains on compatible PR #31 server head `79cab42d43e4d9cdca12b8a1380574f7d40460f6`; Windows `SEC005 TEST` runs the final accepted rotation worker.

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

Certificate rotation is a separate low-frequency LocalSystem worker. It checks authenticated non-secret server certificate status and only invokes full PFX sync when the server thumbprint changes or the local RDP listener drifts.

Admin SSH remains independent. FRP is not active runtime. Each Windows client keeps its own local Ed25519 identity.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, Stage 3 security/device lifecycle, transactional updater rollback, Repair, Defender coexistence, and trusted-certificate CERT-001 through CERT-012 bounded acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted certificate state

The server has one production short-lived Let’s Encrypt public-IP lineage with Hermes-owned renewal scheduling. `SEC005 TEST` currently presents the trusted CUSTOM certificate on the RDP listener and Microsoft Remote Desktop connects without the prior self-signed warning.

The trusted-cert delivery/rollback/reapply path and automatic local-drift recovery are live proven. User chose to keep the certificate representation as-is; no domain/CN cosmetic work is pending.

## CERT-011 — COMPLETE PASS

- authenticated package retrieval/import/binding PASS;
- CNG private key verified non-exportable;
- `NETWORK SERVICE` Read ACL PASS;
- CUSTOM listener binding + TCP 3389 PASS;
- external Microsoft RDP trusted the production certificate;
- corrected type-aware rollback restored exact Windows default self-signed state and warning;
- fixed reapply restored trusted CUSTOM behavior.

## CERT-012 — COMPLETE bounded PASS

- server non-secret state/status + renewal smoke PASS;
- unchanged Windows worker fast path returned `CERT_ROTATION=UNCHANGED`;
- rotation Scheduled Task runs as LocalSystem SID `S-1-5-18`;
- localized Russian `СИСТЕМА` identity handling proved correct;
- global mutex ACL upgrade bug was reproduced, transactional setup rollback passed, and the fixed head was CI/live accepted;
- controlled self-signed drift was detected automatically;
- worker invoked the accepted sync path itself and logged `CERT_ROTATION=UPDATED`;
- expected trusted CUSTOM thumbprint returned;
- TCP 3389 remained listening and worker task stayed Running;
- fresh external Microsoft RDP connected as protected/trusted with no self-signed warning;
- PR #31 merged.

Natural renewal-driven thumbprint rotation is intentionally deferred to a real future renewal event; do not force an extra production issuance only to generate evidence.

## Exact next step

Start CERT-013 from current `main`: integrate the already accepted certificate rotation companion into normal Windows fresh install, transactional update, Repair and uninstall flows so users do not need to run `setup-client-cert-rotation.ps1` manually.
