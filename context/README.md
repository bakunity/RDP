# Hermes RDP Context

This directory is durable engineering context for continuing Hermes RDP work across chats/sessions. It is not a transcript and must never contain secrets.

## Read order

1. `LAST_SESSION.md` — compact handoff delta from the latest work boundary.
2. `ACTIVE_WORK.md` — current active engineering truth and exact acceptance boundary.
3. `CURRENT_STATE.md` — concise product/runtime snapshot.
4. `NEXT_WORK.md` — exact next product work and deferred items.
5. `EVIDENCE_LEDGER.md` — demonstrated PASS/FAIL/root-cause evidence.
6. `DECISIONS.md` — durable architecture/product decisions.
7. `HISTORY.md` — major completed milestones.
8. `PROJECT_HANDOFF.md` — broader project handoff for a new engineering chat.
9. `SESSION_PROTOCOL.md` / `CONTEXT_LIFECYCLE.md` — how to maintain this context.
10. `archive/` — historical full audits; read when detailed provenance is required.

## Current headline

As of 2026-08-14, trusted public-IP RDP certificates and automatic rotation are bounded live-accepted through CERT-012, and CERT-013 normal Windows lifecycle integration has completed all live product gates: transactional Update, targeted Repair, clean Fresh Install, real external trusted Microsoft RDP and normal Uninstall.

Accepted CERT-013 product/test code head before evidence-only commits:

`e11cf89ed26d551ca92b4010034d6e6792a9266b`

Reconcile CI #381 passed Linux full release checks and Windows PowerShell 5.1 validation. Read `ACTIVE_WORK.md` for the exact current PR/merge state rather than relying on this headline.

## Release notes

Release history has its own durable pipeline:

- `docs/releases/UNRELEASED.md` — rolling next-release engineering ledger;
- `docs/releases/vX.Y.Z.md` — compact public GitHub Release notes;
- `docs/releases/history/vX.Y.Z-full.md` — full engineering history for that release.

Keep confirmed work in `UNRELEASED.md` while developing so release descriptions do not have to be reconstructed from memory later.

## Non-negotiable evidence rule

A PASS applies only to the tested build/scenario boundary. Do not rerun already accepted tests without a concrete regression reason, but do create a new revalidation obligation when relevant code changes.

Natural production certificate renewal is currently a deferred observation, not a merge blocker. Do not force unnecessary certificate issuance solely for evidence.

## Secrets rule

Never write private SSH keys, PFX passwords, pairing codes, API/device tokens or similar credentials into context, release notes, commits or chat summaries.
