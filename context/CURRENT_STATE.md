# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` historical packaging-error release; tag is not rewritten.
- PR #28: `v1.2.1` packaging hotfix merged and remains stable.
- PR #29 trusted public-IP server certificate lifecycle is merged as `33c7b6ac6e5a6fb732963988c4734a8a7ef8ec5e`.
- Draft PR #30 is the active Windows certificate delivery/binding work; current head is `83e1b0b5d89b2728646a8eb518026ba9d1cf575a`.

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

Do not repeat without a concrete regression reason: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, Stage 3 security/device lifecycle, transactional updater rollback, Repair, and Defender coexistence.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its deferred exact-Windows one-process observation.

## Trusted certificate state

Server-side trusted public-IP issuance and renewal are accepted. PR #29 productized setup reused the production lineage without changing its serial. Hermes-owned renewal timer/service are active and TCP 80 is free outside ACME operations.

## CERT-010 — PASS

Read-only inventory on non-critical `SEC005 TEST` established Windows 10 Pro 19045 x64 / PowerShell 5.1 x64, default self-signed RDP baseline, TerminalServices CIM availability, rollback thumbprint, certificate tools and TCP 3389 listener.

## CERT-011 — trusted RDP core PASS

Initial PR #30 implementation on `af054274...` passed CI #324 and bounded live server deployment.

On `SEC005 TEST`:

- authenticated certificate package retrieval PASS;
- PFX import PASS;
- CNG private key verified non-exportable;
- NetworkService Read ACL PASS;
- trusted certificate bound as CUSTOM;
- TCP 3389 stayed listening;
- fresh external Microsoft Remote Desktop connection succeeded;
- client reported remote-computer authenticity verified using the server certificate;
- certificate UI showed production Let’s Encrypt issuer `YR1`.

The public-IP trusted-RDP objective is therefore live-proven.

## Rollback correction

The first explicit rollback exposed a confirmed bug: the original Windows default self-signed listener was hash type `1` with no explicit registry binding, but the script tried to restore its thumbprint as a CUSTOM CIM binding and Windows returned `HRESULT 0x80041008`.

Corrected live rollback proved the right behavior:

- custom registry binding removed;
- hash type returned `3 -> 1`;
- exact original self-signed thumbprint returned;
- TCP 3389 remained listening.

PR #30 current head `83e1b0b...` implements type-aware rollback for both explicit and automatic failure paths. CI #333 is PASS on Linux full release checks and Windows PowerShell 5.1.

## Current live Windows state

`SEC005 TEST` is intentionally on the restored Windows default self-signed RDP certificate after the corrected rollback. Trusted certificate remains installed in `LocalMachine\My` and can be re-applied without a new PFX import.

## Exact next step

Open one fresh external Microsoft Remote Desktop connection through the normal Hermes endpoint while in the rolled-back self-signed state. Confirm RDP still connects; the original certificate warning is expected. Then reapply the trusted binding using fixed PR #30 head `83e1b0b...`, confirm CUSTOM + TCP 3389 and one fresh trusted external reconnect. After that PR #30 can become merge-ready.
