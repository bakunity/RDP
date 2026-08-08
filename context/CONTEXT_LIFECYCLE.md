# Hermes RDP — Context Lifecycle & Compaction

Updated: 2026-08-08

Purpose: keep durable project memory useful after months of development. Saving facts is only half of the problem; stale, duplicated and oversized context must be retired deliberately.

## Core principle

The active context is a **working set**, not an append-only archive.

```text
new fact
  -> active working memory
  -> confirmed / implemented / accepted
  -> consolidated
  -> superseded or completed
  -> compacted / archived
```

Git history and `context/archive/` preserve history. Active files should describe the project **now**.

## Three storage temperatures

### HOT — read every project chat

- `ACTIVE_WORK.md`
- `EVIDENCE_LEDGER.md`
- `CURRENT_STATE.md`

Rules:

- current only;
- aggressively remove stale implementation detail;
- no raw transcripts;
- should reconstruct the immediate engineering state in a few minutes.

### WARM — stable guidance

- `PROJECT_HANDOFF.md`
- `NEXT_WORK.md`
- `DECISIONS.md`
- `SESSION_PROTOCOL.md`
- this file

Rules:

- update when architecture, priorities or operating rules change;
- do not mirror temporary PR details already owned by `ACTIVE_WORK.md`;
- completed work leaves `NEXT_WORK.md` instead of accumulating forever.

### COLD — historical material

- `HISTORY.md`
- final release notes
- `context/archive/`
- Git commit history

Rules:

- not read by default;
- may be large;
- never overrides current state;
- used when a future engineer needs old reasoning, evidence boundaries or migration history.

## Canonical ownership — one fact has one primary home

Avoid maintaining several independently editable copies of the same fact.

| Fact type | Canonical active owner |
|---|---|
| active PR/head/deployment/rollback/next exact action | `ACTIVE_WORK.md` |
| runtime PASS/FAIL / confirmed bug / evidence boundary | `EVIDENCE_LEDGER.md` |
| consolidated current product state | `CURRENT_STATE.md` |
| architecture/product identity | `PROJECT_HANDOFF.md` |
| active roadmap / acceptance queue | `NEXT_WORK.md` |
| durable constraints/choices | `DECISIONS.md` |
| release-facing change | current release draft/final release notes |
| old detailed reasoning | `archive/` |

Other files may summarize a canonical fact, but should point to the owner instead of carrying a second detailed version that can drift.

## Fact lifecycle

### 1. HYPOTHESIS

Keep primarily in `ACTIVE_WORK.md` or a current audit.

Do not put an unproven hypothesis into `DECISIONS.md` or present it as PASS in `EVIDENCE_LEDGER.md`.

### 2. CONFIRMED BUG / CONFIRMED FACT

Record durable evidence in `EVIDENCE_LEDGER.md`.

If it blocks current work, summarize it in `ACTIVE_WORK.md`.

### 3. IMPLEMENTED, NOT VALIDATED

Keep in `ACTIVE_WORK.md` and release draft when release-relevant.

Do not replace the original confirmed bug evidence until runtime acceptance exists.

### 4. PASS / CLOSED

- record PASS in `EVIDENCE_LEDGER.md`;
- remove the blocker from `ACTIVE_WORK.md`;
- remove completed work from `NEXT_WORK.md`;
- keep only product-level consequences in `CURRENT_STATE.md`;
- add a milestone to `HISTORY.md` only if significant;
- release-facing result stays in release notes.

### 5. SUPERSEDED

A fact becomes superseded when a newer architecture, implementation or decision makes it no longer current.

Rules:

- remove the obsolete detail from HOT files;
- do not leave two contradictory “current” descriptions;
- if historical reasoning matters, archive it or rely on Git history;
- for a superseded durable decision, keep a short tombstone such as `SUPERSEDED by Decision N on YYYY-MM-DD` until the next compaction, then archive the old detail;
- never silently rewrite historical evidence to pretend the old behavior never existed.

### 6. ARCHIVED

Historical snapshots move under `context/archive/` with a clear header:

```text
Status: HISTORICAL / SUPERSEDED
Captured: YYYY-MM-DD
Superseded by: <current file / release / decision>
Reason retained: <why it may still be useful>
```

Archive files are not part of default context loading.

## What gets deleted vs archived

### Rewrite/delete from active context

Safe to remove from active files when no longer useful:

- old exact PR head after the workstream changed;
- completed TODOs;
- obsolete next-step instructions;
- disproven hypotheses;
- temporary diagnostic commands;
- old UI examples replaced by the actual implementation;
- repeated descriptions of the same PASS;
- stale `LAST_SESSION` detail already represented in HOT files.

The Git history preserves the previous version.

### Archive explicitly

Archive when the removed material has future explanatory value:

- deep architecture/product audits;
- major migration reasoning;
- release acceptance snapshots;
- evidence ledgers before large compaction;
- superseded architecture decisions whose rationale may matter later;
- incident/root-cause reports worth retaining.

Do **not** archive routine debugging noise just because it existed.

## Evidence-ledger growth strategy

`EVIDENCE_LEDGER.md` must not grow forever line-by-line across every release.

At a stable release or major milestone:

1. save a release evidence snapshot, for example:
   `context/archive/releases/v1.2.0-evidence.md`;
2. preserve immutable IDs/evidence in that snapshot;
3. compact the active ledger into:
   - current product guarantees/baseline PASS;
   - unresolved confirmed bugs;
   - current-release acceptance;
4. older low-level evidence is referenced by release snapshot instead of duplicated;
5. if a later change can regress an old guarantee, create a fresh acceptance entry for the changed build.

This preserves proof without forcing every future chat to read years of tests.

## Decision growth strategy

`DECISIONS.md` contains **currently applicable durable decisions**, not the complete history of all opinions.

When a decision changes:

1. record the new decision and reason;
2. mark the old one `SUPERSEDED` with successor/date;
3. after the new decision has stabilized, move old detailed rationale to archive if still valuable;
4. keep Git history as the default historical record.

Do not keep mutually incompatible decisions as if both still apply.

## Audit rotation

`LATEST_AUDIT.md` means exactly one current deep audit.

When a newer deep audit replaces it:

1. move/copy the old audit to `context/archive/YYYY-MM-DD-<topic>-audit.md` if worth retaining;
2. write the new audit to `LATEST_AUDIT.md`;
3. old audit TODOs must never remain in the default reading path as current work.

If no current deep audit is needed, `LATEST_AUDIT.md` may be a short pointer to archived audits and current HOT files.

## LAST_SESSION lifecycle

`LAST_SESSION.md` is deliberately disposable.

- keep only the latest intentional chat-boundary delta;
- once its facts are represented in HOT/WARM files, compact it to a short pointer or replace it at the next handoff;
- do not archive every session;
- archive only an unusually valuable session analysis that is not already preserved elsewhere.

## Soft size budgets

These are hygiene thresholds, not CI-hard limits. Crossing them triggers compaction before more context is added.

| File | Soft budget |
|---|---:|
| `README.md` | ~200 lines |
| `ACTIVE_WORK.md` | ~200 lines |
| `CURRENT_STATE.md` | ~350 lines |
| `NEXT_WORK.md` | ~300 lines |
| `PROJECT_HANDOFF.md` | ~250 lines |
| `DECISIONS.md` | ~300 lines |
| `EVIDENCE_LEDGER.md` | ~400 lines before release rotation |
| `LATEST_AUDIT.md` | ~500 lines; archive/replace if larger |
| `LAST_SESSION.md` | ~150 lines |

A file being under budget does not make stale content acceptable. A file being over budget is not automatically wrong if the material is truly active, but it requires review.

## Compaction triggers

Run a context compaction when any of these happens:

- a release is published;
- a major PR/workstream is merged, closed or abandoned;
- architecture changes materially;
- a HOT/WARM file exceeds its soft budget;
- a current file contains completed TODOs or obsolete branch/deployment details;
- two context files contradict one another;
- `LATEST_AUDIT` is no longer latest;
- the active evidence ledger becomes difficult to scan;
- the project moves to a new phase (for example stabilization -> docs/release).

Compaction is a normal operation, not data loss.

## Context health audit

Periodically, and always at release/milestone boundaries, check:

1. Can a new chat identify the exact current stage in under two minutes?
2. Does `ACTIVE_WORK` match current GitHub/deployment truth?
3. Are old blockers removed after PASS?
4. Does `NEXT_WORK` contain only remaining work?
5. Does `CURRENT_STATE` contradict `EVIDENCE_LEDGER` anywhere?
6. Are mutable refs/SHAs clearly distinguished from durable facts?
7. Are release notes supported by evidence rather than memory?
8. Are superseded decisions clearly retired?
9. Is historical detail out of the default reading path?
10. Are any secrets/production-sensitive values present unnecessarily?
11. Are the HOT files within reasonable size and free of repetition?
12. Would losing the current chat right now still leave enough state to continue?

If any answer is “no”, fix context before accumulating another large work-unit.

## Release-boundary garbage collection

At release `vX.Y.Z`:

```text
freeze evidence snapshot -> archive/releases/vX.Y.Z-evidence.md
finalize release notes
compact ACTIVE_WORK for next workstream
compact EVIDENCE_LEDGER to baseline + open acceptance
rewrite CURRENT_STATE to released truth
remove completed items from NEXT_WORK
retire superseded decisions
archive obsolete deep audit
append one HISTORY milestone
reset/compact LAST_SESSION
```

The goal is that the next release starts with a small, accurate working set rather than inheriting all temporary detail from the previous cycle.

## Git history is part of the memory design

Do not keep stale text in active files merely because removing it feels like losing information.

Every context-only commit is versioned. If a future engineer needs the exact previous wording, Git history exists. `archive/` is reserved for historically useful snapshots, not every deleted paragraph.

## Anti-patterns

Do not:

- append forever to every file;
- keep completed TODOs “for history” in `NEXT_WORK`;
- keep a confirmed-fixed bug as an active blocker;
- duplicate exact branch/head/deployment state across five files;
- archive every terminal command;
- let `LATEST_AUDIT` become a museum of old audits;
- preserve contradictory active decisions;
- mark old evidence false merely because behavior was later changed;
- rely on age alone: an old architectural decision may still be fully current, while a five-minute-old PR SHA may already be stale.

## Freshness is semantic, not chronological

A context item is stale when it no longer describes current truth or current work — not simply because it is old.

Examples:

- `OpenSSH replaced FRP` can remain current for years.
- an active PR SHA can be stale after one commit.
- a PASS from an old release remains valid as historical baseline, but may require re-acceptance if relevant code changes.
- an old bug report becomes historical after the fix is live-accepted.

This distinction is required for reliable long-term project memory.