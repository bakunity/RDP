# Hermes RDP — persistent project context

This folder is the durable project memory. Development must not depend on the current ChatGPT conversation retaining every detail.

> **New chat / recovered session:** read this file first, then follow the order below. Before changing code or infrastructure, compare context with current GitHub PRs/branches/releases and real runtime evidence.

## Core model

```text
chat                  = temporary working memory
runtime / CI           = evidence
GitHub context         = durable working memory
Git history / archive  = historical memory
```

Do **not** wait until the end of a chat to save important state. Context updates are event-driven after meaningful engineering work-units.

Also do **not** let context grow forever. Active context is a working set: stale/completed/superseded material is compacted or archived according to [`CONTEXT_LIFECYCLE.md`](CONTEXT_LIFECYCLE.md).

## Reading order

### HOT — always read

1. [`ACTIVE_WORK.md`](ACTIVE_WORK.md) — active PR/head, deployment truth, current blockers, implemented-but-unvalidated work, exact next step.
2. [`EVIDENCE_LEDGER.md`](EVIDENCE_LEDGER.md) — durable PASS/FAIL/confirmed-root-cause ledger.
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — consolidated current product state.

### WARM — read before changing direction

4. [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) — stable architecture/product vector.
5. [`NEXT_WORK.md`](NEXT_WORK.md) — remaining roadmap and acceptance queue.
6. [`DECISIONS.md`](DECISIONS.md) — currently applicable durable decisions.
7. [`SESSION_PROTOCOL.md`](SESSION_PROTOCOL.md) — checkpoint rules during work.
8. [`CONTEXT_LIFECYCLE.md`](CONTEXT_LIFECYCLE.md) — stale-context retirement, compaction, archive and size policy.

### COLD / historical — only when needed

9. [`LATEST_AUDIT.md`](LATEST_AUDIT.md) — latest deep audit only; may be a pointer if no current deep audit exists.
10. [`LAST_SESSION.md`](LAST_SESSION.md) — optional latest chat-boundary delta; not authoritative.
11. [`HISTORY.md`](HISTORY.md) — major milestones only.
12. [`archive/README.md`](archive/README.md) — index/rules for historical snapshots.

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
LATEST_AUDIT / LAST_SESSION
        ↓
archive / old Git history
```

A context edit cannot turn an untested implementation into a PASS.

## Canonical ownership

| Information | Primary owner |
|---|---|
| active PR/head, deployed truth, rollback point, exact next action | `ACTIVE_WORK.md` |
| live PASS/FAIL, confirmed bug/root cause, evidence boundary | `EVIDENCE_LEDGER.md` |
| consolidated current product state | `CURRENT_STATE.md` |
| architecture / product vector | `PROJECT_HANDOFF.md` |
| durable architectural/product decision | `DECISIONS.md` |
| remaining priorities / acceptance queue | `NEXT_WORK.md` |
| release-facing changes | active release draft under `docs/releases/` |
| large milestone | `HISTORY.md` |
| old detailed reasoning/evidence snapshot | `archive/` |
| optional chat-boundary delta | `LAST_SESSION.md` |

Summaries may appear elsewhere, but one fact should have one detailed canonical owner so multiple copies cannot drift independently.

## Continuous checkpoint triggers

Checkpoint context after a meaningful work-unit, especially when:

- a live acceptance becomes PASS/FAIL;
- a hypothesis becomes a confirmed root cause;
- a fix reaches code + green CI;
- server/client deployment changes what is actually running;
- a rollback point changes;
- a durable architecture/product decision changes;
- the exact next engineering stage changes.

Do not checkpoint every command. Preserve the resulting engineering truth.

## Continuous cleanup triggers

Compact/retire stale context when:

- a release is published;
- a PR/workstream is merged, closed or abandoned;
- architecture changes;
- active files become difficult to scan or exceed soft budgets;
- completed TODOs remain in current work files;
- current files contradict one another;
- `LATEST_AUDIT` is no longer latest;
- the project enters a new phase.

See `CONTEXT_LIFECYCLE.md` for exact rules. Removing stale text from an active file is **not data loss**: Git history exists, and historically valuable snapshots go to `archive/`.

## Branch policy

Product code normally stays in feature branches/PRs.

Context-only checkpoint/compaction commits may go directly to `main` while a product PR is open. This is intentional so a future chat can reconstruct active work from the default branch.

Context must clearly distinguish:

- merged vs unmerged;
- deployed vs branch-only;
- PASS vs implemented-not-validated;
- mutable current refs vs durable facts.

## Release-cycle memory model

```text
EVIDENCE_LEDGER = engineering proof
ACTIVE_WORK     = operational checkpoint
PR body         = live scope + merge gate
release draft   = future changelog
CURRENT_STATE   = consolidated truth
archive         = retired historical detail
```

At a release boundary, freeze a release evidence snapshot, compact the active ledger/state/work queue, finalize release notes and start the next cycle with a small working set.

## Repository

- Project: `bakunity/RDP`
- Product: **Hermes RDP**
- Context initialized: 2026-08-07
- Continuous checkpoint model: 2026-08-08
- Lifecycle/compaction model: 2026-08-08

## Suggested prompt for a new chat

> Открой `context/README.md` в `bakunity/RDP`. Сначала прочитай `ACTIVE_WORK.md`, `EVIDENCE_LEDGER.md` и `CURRENT_STATE.md`, затем нужные WARM-файлы. Сверь их с текущим GitHub PR/release/ветками. Назови активный этап, последние реальные PASS/FAIL, что реализовано, но ещё не проверено, и точный следующий шаг. Не повторяй подтверждённые проверки без regression-причины и не используй архив как current truth.

## Sensitive information

Never store in public context:

- passwords;
- Telegram bot tokens or unnecessary numeric owner IDs;
- pairing codes;
- private SSH keys;
- device/API tokens;
- ready-to-use secret fingerprints;
- secret configs;
- unnecessary production public IPs.

Use placeholders when an identifier is not required for understanding.