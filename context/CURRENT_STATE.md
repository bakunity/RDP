# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` historical packaging-error release; tag is not rewritten.
- PR #28: `v1.2.1` packaging hotfix merged and remains stable.
- PR #29 trusted public-IP certificate lifecycle has completed CI and immutable live acceptance; it is ready for merge/reconciliation.

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

Admin SSH remains independent from Hermes tunnel SSH. FRP is not active runtime. Each Windows client keeps its own local Ed25519 identity.

## Live deployment truth

- Production controller still runs accepted PR #25 head `0e2e7aef77ab1df804b70d9fd29d4b5736fbac60`.
- Certificate lifecycle setup did not redeploy the controller or dedicated sshd product code.
- `SEC005 TEST` remains the first non-critical Windows fixture for future certificate binding.

## Accepted stabilization baseline

Do not repeat without a concrete regression reason:

- external Microsoft RDP through Hermes;
- multi-device simultaneous operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell/Sysnative;
- Telegram OFF/ON/RESTART and automatic dashboard refresh;
- Stage 3 security/device lifecycle acceptance;
- transactional server/Windows updater rollback acceptance;
- existing-device Repair acceptance;
- Microsoft Defender real-time protection coexistence.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its deferred exact-Windows one-process observation.

## Current certificate state

Trusted-certificate track targets the existing public IPv4, not a cosmetic domain.

Server-side issuance and renewal are accepted:

- Certbot 5.7.0 under `/opt/certbot`;
- public HTTP-01 reachability through UFW/TCP 80: PASS;
- staging public-IP issuance: PASS;
- key/fullchain and renewal dry-run mechanics: PASS;
- production Let’s Encrypt public-IP issuance: PASS;
- production issuer, IP SAN, Server Authentication EKU, RSA 2048, certificate/key match and local trust verification confirmed;
- Hermes-owned renewal service/timer enabled and active;
- bounded renewal service execution returns success and does not renew early;
- TCP 80 is free after lifecycle operations.

CERT-009 productization live acceptance is PASS on immutable PR #29 head `e914a0f45a6cc734d25b02340353fc06ace6c7c8`:

- existing production lineage was reused;
- certificate serial before/after was identical;
- no new certificate request occurred;
- trusted-certificate config/marker was written correctly;
- repository-owned renewal timer remained enabled/active;
- renewal smoke returned `PASS_NOT_DUE`;
- TCP 80 remained free;
- rollback backup existed before adoption.

No Windows RDP listener certificate binding has changed yet.

## Windows delivery security boundary

Current Hermes device authentication already provides useful primitives for CERT-010:

- per-device bearer token generated with high entropy at pairing;
- only SHA-256 token hash stored server-side;
- constant-time token-hash comparison during authentication;
- Windows API client pins the server TLS certificate fingerprint;
- Windows local `device.json`, SSH private key and `known_hosts` are ACL-restricted to SYSTEM and Administrators.

A Windows certificate package must therefore travel only through the existing pinned HTTPS + authenticated device channel, never through a static/public URL.

For the scalable model, one short-lived public-IP lineage is shared per Hermes server. Separate public certificates per Windows device do not scale because every device uses the same public-IP identifier set and CA duplicate/exact-set issuance limits apply.

## Exact next step

Merge/reconcile PR #29 after its PASS gate, then start **CERT-010** with a read-only inventory on `SEC005 TEST` before any listener mutation:

- current `Win32_TSGeneralSetting` RDP listener certificate hash/hash type;
- current certificate object represented by that hash, if present;
- TermService state;
- availability of the TerminalServices CIM provider;
- LocalMachine certificate-store behavior required for non-exportable PFX import and rollback.

Only after that inventory implement authenticated certificate package delivery, non-exportable LocalMachine import, NETWORK SERVICE private-key read ACL, thumbprint binding and deterministic rollback.
