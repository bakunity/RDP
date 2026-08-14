# Hermes RDP — Current State Snapshot

Updated: 2026-08-14

For immediate operational truth read `ACTIVE_WORK.md`; for detailed historical proof read `EVIDENCE_LEDGER.md`.

## Repository / release

- Stable published release: **v1.2.1**.
- CERT-001 through CERT-013 bounded behavior is implemented, live accepted where environment-dependent, and merged into `main`.
- PR #33 reconciled core install/architecture/security/operations/validation docs; CI #418 PASS and merged.
- PR #34 reconciled README/public site and removed stale `1.1.0`/obsolete validation copy; CI #420 PASS and merged.
- Next release boundary selected: **v1.3.0** because trusted RDP certificates are a new backward-compatible product capability.
- Draft PR #35 prepares the full v1.3.0 release tree.
- Initial release head `13e2716276177849cb02a42864f824747537d88f`: CI #422 PASS.
- Reconciled pre-approval head `8555aa3977f0f954f11fdf944a5ebedeeb3d815c`: CI #424 PASS on Linux full release checks + Windows PowerShell 5.1.
- PR #35 remains draft. Merge triggers automatic immutable tag/GitHub Release publication and requires explicit approval.

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

Certificate rotation is a separate low-frequency LocalSystem worker. It checks authenticated non-secret server certificate status and only invokes full PFX sync on thumbprint change/local listener drift. Certificate work stays outside the 3-second main Agent loop.

Admin SSH remains independent. FRP is not active runtime. Each Windows client keeps its own Ed25519 identity.

## Accepted baseline

Do not repeat without concrete regression evidence: external RDP, multi-device isolation, Windows/Linux reboot recovery, Windows Server 2019, Win10 x64 + x86 PowerShell/Sysnative, Telegram control/UI, transactional updater rollback, existing-device Repair, Defender coexistence, CERT-001 through CERT-012, and full CERT-013 lifecycle acceptance.

SEC-004 remains intentionally fixture-unavailable. RL-006 remains PARTIAL PASS only for its optional deferred exact-Windows one-process observation.

## Trusted certificate state

The server has a production short-lived Let’s Encrypt public-IP lineage with Hermes-owned renewal scheduling. Accepted Windows fixtures present the trusted CUSTOM certificate and Microsoft Remote Desktop connects without the previous self-signed warning.

Normal Windows Fresh Install, Update and Repair manage the certificate rotation companion automatically; Uninstall removes its runtime along with the main Hermes client runtime.

Natural renewal-driven thumbprint rotation remains deferred to the real next renewal; do not force extra production issuance for evidence.

## v1.3.0 candidate boundary

v1.3.0 is a release cut of already accepted merged behavior plus release/docs/presentation metadata. No intentional breaking change relative to v1.2.1.

Trusted RDP certificate lifecycle remains optional and requires a globally routable public IPv4 plus reachable TCP 80 for ACME HTTP-01 when enabled.

The release candidate uses concise public notes plus a separate long-form engineering history.

## Exact next step

Wait for explicit publication approval. On approval, reconcile latest `main` context into PR #35 one final time, rerun exact-head CI, then mark ready/merge with exact-head guard and verify tag/Release publication.
