# Hermes RDP — Active Work

Updated: 2026-08-15

## Repository / release

- Repository: `bakunity/RDP`.
- Stable published release: **v1.3.0**; historical tag/history remain immutable.
- Active product PR: **#37 `feat: add zero-config server installer`**.
- PR #37 is **ready for review** and remains unmerged.
- Runtime-accepted product-code boundary: `056bf7473ff851157f4c749f233fb0fb8b57a133`; CI #459 PASS on Linux full release checks and Windows PowerShell 5.1.
- Acceptance/context cleanup commit `ff264100b231c3f90269c3e8fa17bda5e4d2aab2` removed the temporary clean-reinstall helper and passed CI #460.
- Merge requires explicit user approval plus a green check on the current exact head.

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

Trusted-RDP certificate lifecycle remains a separate low-frequency path outside the 3-second Agent loop.

## Accepted baseline — do not repeat without regression evidence

- external Microsoft RDP through Hermes;
- simultaneous multi-device operation and failure isolation;
- Windows/Linux reboot recovery;
- Windows Server 2019;
- Win10 x64 + x86 PowerShell / Sysnative OpenSSH compatibility;
- Telegram OFF/ON/RESTART and status UX;
- transactional Linux and Windows updater rollback;
- existing-device Repair success/rollback;
- Defender coexistence without exclusions/disablement;
- trusted public-IP certificate lifecycle CERT-001 through CERT-013.

## PR #37 zero-config server onboarding — accepted

Normal-user flow:

```text
one curl command
→ Debian/Ubuntu + APT preflight/repair
→ public IPv4 detection
→ masked Telegram bot-token input
→ private one-time /claim owner binding
→ immutable source resolution
→ core Hermes install
→ automatic trusted public-IP certificate lifecycle
→ Telegram /start
```

Live Debian 13 Trixie acceptance confirms stale archive repair, semantic overlapping APT component normalization with rollback, masked token entry, secure Telegram claim, normal dashboard, exact source resolution, full clean-state reinstall, active Hermes sshd/controller, nginx coexistence, trusted certificate lifecycle and `=== HERMES RDP READY ===`.

An interruption while waiting for the owner claim after a clean purge left no partially installed Hermes core; rerunning the normal installer succeeded because claim precedes core mutation.

The temporary clean-reinstall acceptance helper is no longer shipped in the PR.

## Exact next action

Await explicit user merge approval. Before merging, verify PR #37 still points to the expected current head and its required CI is green. Then merge without rewriting historical release tags.

Natural renewal-driven certificate rotation remains a deferred operational observation, not a blocker. SEC-004 remains fixture-unavailable. RL-006 remains PARTIAL only for its optional original-fixture one-process observation.

Never store bot tokens, private keys, PFX passwords, device/API tokens, one-time claim/pair codes, unnecessary production IPs, certificate package secrets or personal numeric IDs in context.
