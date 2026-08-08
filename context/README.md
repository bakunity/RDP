# Hermes RDP — persistent project context

This folder is the durable project memory. It exists specifically so development does **not** depend on the current ChatGPT conversation retaining every detail.

> **New chat / recovered session:** read this file first, then follow the order below. Before changing code or infrastructure, compare the context with current GitHub PRs/branches/releases and real runtime evidence.

## Core rule

Do **not** wait until the end of a chat to save important context.

The conversation is temporary working memory. GitHub context is durable project memory.

Context updates are **event-driven**, not message-count-driven:

```text
meaningful engineering event
        ↓
checkpoint durable facts in context/
        ↓
continue development
```

A meaningful event includes a live PASS/FAIL, confirmed bug/root cause, code+CI work-unit, deployment state change, durable decision, or a change to the exact next engineering target.

## Reading order

### Hot operational context — always read

1. [`ACTIVE_WORK.md`](ACTIVE_WORK.md) — what is happening **right now**: active PR/head, deployment truth, confirmed blockers, implemented-but-unvalidated work and exact next step.
2. [`EVIDENCE_LEDGER.md`](EVIDENCE_LEDGER.md) — durable acceptance ledger: what is actually PASS/FAIL/CONFIRMED and what must not be repeatedly re-proved.
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — current product-level snapshot.

### Stable project context — read before changing direction

4. [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) — architecture, product vector and major engineering context.
5. [`NEXT_WORK.md`](NEXT_WORK.md) — priorities, remaining acceptance and target release direction.
6. [`DECISIONS.md`](DECISIONS.md) — durable architectural/product constraints that future work should not casually reverse.

### Historical / deep context — read when needed

7. [`LATEST_AUDIT.md`](LATEST_AUDIT.md) — latest deep audit and reasoning snapshot.
8. [`LAST_SESSION.md`](LAST_SESSION.md) — compact boundary handoff from a completed/paused long chat. **Useful, but no longer authoritative for active state.**
9. [`HISTORY.md`](HISTORY.md) — major milestones only.
10. [`SESSION_PROTOCOL.md`](SESSION_PROTOCOL.md) — exact continuous checkpoint rules.
11. [`archive/`](archive/) — historical full snapshots; never assume archive TODO/status is current.

## Truth priority

When sources disagree:

```text
real runtime evidence / current GitHub
        ↓
ACTIVE_WORK.md
        ↓
EVIDENCE_LEDGER.md
        ↓
CURRENT_STATE.md
        ↓
PROJECT_HANDOFF / NEXT_WORK / DECISIONS
        ↓
LAST_SESSION / LATEST_AUDIT
        ↓
archive
```

`PASS` still requires evidence. A newer context file cannot turn an untested implementation into a PASS.

## What gets written where

| Information | File |
|---|---|
| active PR/head, deployment truth, current blockers, exact next action | `ACTIVE_WORK.md` |
| live PASS/FAIL, confirmed bug/root cause, evidence boundary | `EVIDENCE_LEDGER.md` |
| consolidated product state | `CURRENT_STATE.md` |
| architecture / product vector | `PROJECT_HANDOFF.md` |
| durable architectural/product decision | `DECISIONS.md` |
| priorities / acceptance queue | `NEXT_WORK.md` |
| release-facing changes | active release draft under `docs/releases/` |
| large milestone | `HISTORY.md` |
| chat-boundary delta | `LAST_SESSION.md` |

Do not duplicate raw logs everywhere. One fact may be summarized in `ACTIVE_WORK` and permanently indexed in `EVIDENCE_LEDGER`, while detailed raw evidence remains in the conversation/PR discussion when needed.

## Continuous checkpoint policy

Checkpoint context **immediately after a completed work-unit**, especially after:

- a live acceptance test;
- a bug changes from hypothesis to confirmed;
- a fix changes from implemented to live-accepted;
- code + CI changes the active branch head materially;
- server/client deployment changes what is actually running;
- rollback point changes;
- a durable architecture/product decision is made;
- the next engineering stage changes.

Additional safety rule: do not allow a long sequence of meaningful state-changing work to accumulate only in chat. If several relevant changes happen close together, make one compact context checkpoint covering the resulting state.

## Context branch policy

Product code should normally stay in feature branches/PRs.

Operational context files are allowed to receive **context-only commits directly on `main` while a product PR is still open**. This is intentional: a new chat must be able to reconstruct active work from the default branch even if the product PR is not merged yet.

Context files may reference an unmerged PR/branch and must clearly label:

- deployed vs not deployed;
- confirmed vs implemented-not-validated;
- current branch/head when useful.

## Release tracking

During a release/stabilization cycle:

```text
EVIDENCE_LEDGER      = engineering proof
ACTIVE_WORK          = current operational checkpoint
PR body              = live scope + acceptance gate
release draft        = future user-facing changelog
CURRENT_STATE        = consolidated project truth
```

This prevents release notes from being reconstructed from memory at the end.

## Existing historical audit

A detailed source snapshot exists at:

- [`archive/2026-08-07-full-product-audit.md`](archive/2026-08-07-full-product-audit.md)

It is historical evidence/reasoning, not current state.

## Repository

- Project: `bakunity/RDP`
- Product: **Hermes RDP**
- Current published OpenSSH transition release at context initialization: `v1.1.0`
- Context system initialized: 2026-08-07
- Continuous checkpoint model introduced: 2026-08-08

## Suggested prompt for a new chat

> Открой `context/README.md` в `bakunity/RDP`. Сначала прочитай `ACTIVE_WORK.md`, `EVIDENCE_LEDGER.md` и `CURRENT_STATE.md`, затем остальные файлы по порядку. Сверь это с текущим GitHub PR/release/ветками. Назови текущий активный этап, последние реальные PASS/FAIL, что реализовано, но ещё не проверено, и точный следующий шаг. Не повторяй уже подтверждённые проверки без причины.

## Sensitive information

Never store in public context:

- passwords;
- Telegram bot tokens or unnecessary numeric owner IDs;
- pairing codes;
- private SSH keys;
- device/API tokens;
- ready-to-use secret fingerprints;
- secret configs;
- production public IPs when unnecessary.

Use placeholders when an identifier is not required for understanding.