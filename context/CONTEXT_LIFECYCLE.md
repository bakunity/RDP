# Hermes RDP — Context Lifecycle

## Purpose

Keep project context useful across long chats without turning the repository into a transcript dump.

## Canonical layers

- `ACTIVE_WORK.md`: immediate engineering truth.
- `CURRENT_STATE.md`: concise product/runtime snapshot.
- `NEXT_WORK.md`: remaining product work only.
- `EVIDENCE_LEDGER.md`: proved facts, failures and revalidation boundaries.
- `DECISIONS.md`: durable architecture/product decisions.
- `HISTORY.md`: major completed milestones.
- `LAST_SESSION.md`: compact chat-boundary delta; non-authoritative when it conflicts with the canonical files above.
- `PROJECT_HANDOFF.md`: broader new-chat handoff.
- `archive/`: full audits/history when detailed provenance is needed.

## Update triggers

Update context after:

- a bounded live PASS/FAIL;
- a confirmed root cause;
- a material architecture decision;
- a PR merge/deploy provenance change;
- a change to the exact next step;
- a chat migration/handoff.

Do not rewrite accepted historical evidence merely because later code exists. A later relevant code change creates a revalidation obligation; it does not erase the earlier PASS.

## Release-note companion process

Engineering work that may matter to a future release must also be accumulated in `docs/releases/UNRELEASED.md` while it happens.

At release time:

- keep the public GitHub Release body compact in `docs/releases/vX.Y.Z.md`;
- preserve detailed engineering history in `docs/releases/history/vX.Y.Z-full.md`;
- never reconstruct the release solely from chat memory.

## Current acceptance example

CERT-013 is an example of the intended evidence model:

- accepted product/test code head `e11cf89ed26d551ca92b4010034d6e6792a9266b`;
- CI #381 Linux + Windows PowerShell 5.1 PASS;
- bounded live acceptance covers Update, Repair, clean Fresh Install, real external trusted RDP and normal Uninstall;
- later evidence/context/release-only commits do not invalidate that product/test code boundary.

## Compaction rule

Prefer durable conclusions over raw logs. Keep exact markers/SHAs/fixture names only when they are needed to prove or resume work. Do not copy entire terminal transcripts into context when a concise accepted boundary is enough.

## Secrets rule

Never store private SSH keys, PFX passwords, pairing codes, device/API tokens or similar credentials in context, release notes, commit messages or chat handoffs.
