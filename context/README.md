# Hermes RDP Context

This directory stores durable engineering context for continuing Hermes RDP work across chats/sessions. It is not a transcript and must never contain secrets.

## Read order

1. `LAST_SESSION.md` — compact latest handoff delta.
2. `ACTIVE_WORK.md` — immediate engineering truth and exact acceptance boundary.
3. `CURRENT_STATE.md` — concise runtime/product snapshot.
4. `NEXT_WORK.md` — exact remaining work.
5. `EVIDENCE_LEDGER.md` — proved PASS/FAIL/root-cause evidence.
6. `DECISIONS.md` — durable architecture/product decisions.
7. `HISTORY.md` — major completed milestones.
8. `PROJECT_HANDOFF.md` — broad new-chat handoff.
9. `SESSION_PROTOCOL.md` / `CONTEXT_LIFECYCLE.md` — maintenance rules.
10. `archive/` — historical audits/provenance only.

## Current headline

As of 2026-08-14, trusted public-IP RDP certificates and automatic rotation are bounded live-accepted through CERT-012. CERT-013 normal Windows lifecycle integration has also completed all bounded live product gates: transactional Update, targeted Repair, clean Fresh Install, real external trusted Microsoft RDP and normal Uninstall.

Accepted CERT-013 product/test code head before later evidence-only commits:

`e11cf89ed26d551ca92b4010034d6e6792a9266b`

Reconcile CI #381 passed Linux full release checks and Windows PowerShell 5.1 validation. Read `ACTIVE_WORK.md` for the exact current PR/merge state.

## Release notes

- `docs/releases/UNRELEASED.md` — rolling next-release engineering ledger.
- `docs/releases/vX.Y.Z.md` — compact public GitHub Release notes.
- `docs/releases/history/vX.Y.Z-full.md` — detailed engineering history.

Record confirmed release-relevant work continuously so release descriptions never have to be reconstructed from memory.

## Evidence rule

A PASS applies only to the tested build/scenario boundary. Do not rerun accepted tests without a concrete regression reason. Relevant later product-code changes create a new revalidation obligation; docs/context-only changes do not.

Natural production certificate renewal is a deferred observation, not a merge blocker. Do not force unnecessary certificate issuance solely for evidence.

## Secrets rule

Never write private SSH keys, PFX passwords, pairing codes, API/device tokens or similar credentials into context, release notes, commits or chat summaries.
