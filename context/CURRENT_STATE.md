# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- PR #19–#25: merged and live-accepted stabilization work.
- PR #26: documentation reconciliation merged.
- PR #27: `v1.2.0` historical packaging-error release; tag is not rewritten.
- PR #28: `v1.2.1` packaging hotfix merged and remains stable.
- Draft PR **#29** is the active trusted-certificate productization PR.

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
- Certificate setup did not redeploy the controller or dedicated sshd product code.
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

Trusted-certificate track targets the existing **public IPv4**, not a cosmetic domain.

Server-side issuance evidence is complete:

- Certbot 5.7.0 under `/opt/certbot`;
- public HTTP-01 reachability through UFW/TCP 80: PASS;
- staging public-IP issuance: PASS;
- staging key/fullchain/renewal dry-run mechanics: PASS;
- real production Let’s Encrypt public-IP issuance: PASS;
- production issuer, IP SAN, Server Authentication EKU, RSA 2048, certificate/key match and local trust verification confirmed.

Automatic renewal is now also live-proven:

- initial scheduler inventory found no automatic renewal;
- Hermes-owned `hermes-rdp-cert-renew.service` and `.timer` were installed;
- unit verification PASS;
- timer enabled/active with twice-daily schedule, randomized delay and persistence;
- bounded manual service run returned success without early renewal;
- TCP 80 remained free.

No Windows RDP listener certificate binding has changed yet.

## Productization state

Draft PR **#29** (`feat/trusted-rdp-cert-lifecycle`) head `e914a0f45a6cc734d25b02340353fc06ace6c7c8` contains the repository-owned lifecycle module and explicit installer opt-in `--trusted-rdp-cert`.

CI #313 and CI #316 both passed Linux and Windows PowerShell 5.1 validation. PR #29 has not been deployed yet.

The default install remains unchanged: trusted public-IP certificate setup is opt-in until bounded live acceptance completes.

## Architecture constraint

A separate public certificate/key per Windows device would keep private keys local, but all devices use the same public-IP identifier and Let’s Encrypt limits new certificates for the exact same identifier set. This does not scale as the default multi-device Hermes design.

The current scalable direction is one short-lived public-IP lineage per Hermes server plus an authenticated Windows distribution/rotation mechanism. The Windows-facing private-key path remains security-sensitive and is not implemented yet.

## Exact next step

Complete **CERT-009 live acceptance** of PR #29 on the current certificate host. The immutable setup module must reuse the already-valid production certificate, adopt the repository-owned renewal wrapper/units, update Hermes config/marker, pass its renewal smoke test, preserve the certificate serial, and leave TCP 80 free.

Only after this live acceptance proceed to Windows delivery/rotation and first listener binding on `SEC005 TEST` with rollback preserved.
