# Hermes RDP — Context Lifecycle & Compaction

Updated: 2026-08-08

Purpose: keep durable project memory useful after months of development. Saving facts is only half the problem; stale, duplicated, invalidated and oversized context must be retired deliberately.

## Core principle

The active context is a **working set**, not an append-only archive.

```text
new fact
  -> active working memory
  -> confirmed / implemented / accepted
  -> consolidated
  -> superseded / completed / invalidated-for-current-build
  -> compacted / archived
```

Git history and selected `context/archive/` snapshots preserve history. Active files describe the project **now**.

## Three storage temperatures

### HOT — read every project chat

- `ACTIVE_WORK.md`
- `EVIDENCE_LEDGER.md`
- `CURRENT_STATE.md`

Rules:

- current only;
- aggressively retire stale operational detail;
- no raw transcripts;
- enough to reconstruct immediate engineering state in a few minutes.

### WARM — stable guidance

- `PROJECT_HANDOFF.md`
- `NEXT_WORK.md`
- `DECISIONS.md`
- `SESSION_PROTOCOL.md`
- this file

Rules:

- update when architecture, priorities or operating rules change;
- do not mirror temporary PR details already owned by `ACTIVE_WORK`;
- completed work leaves `NEXT_WORK`.

### COLD — historical material

- `HISTORY.md`
- final release notes
- `context/archive/`
- Git commit history

Rules:

- not read by default;
- may be large;
- never overrides current state;
- used only when old reasoning/evidence/migration history is needed.

## Canonical ownership — one primary home per fact

| Fact type | Canonical active owner |
|---|---|
| active PR/head/deployment/rollback/exact next action | `ACTIVE_WORK.md` |
| runtime PASS/FAIL / confirmed bug / evidence boundary / revalidation | `EVIDENCE_LEDGER.md` |
| consolidated current product state | `CURRENT_STATE.md` |
| architecture/product identity | `PROJECT_HANDOFF.md` |
| remaining roadmap/acceptance | `NEXT_WORK.md` |
| durable constraints/choices | `DECISIONS.md` |
| release-facing change | release draft/final release notes |
| old detailed reasoning | `archive/` / Git history |

Other files may summarize, but should not maintain another detailed editable copy.

## Fact lifecycle

### HYPOTHESIS

Keep in `ACTIVE_WORK` or a current audit. Do not present as PASS or durable decision.

### CONFIRMED BUG / CONFIRMED FACT

Record evidence in `EVIDENCE_LEDGER`. If currently blocking work, summarize in `ACTIVE_WORK`.

### IMPLEMENTED, NOT VALIDATED

Keep in `ACTIVE_WORK` and release draft when release-relevant. Do not erase the original bug evidence until runtime acceptance exists.

### PASS / CLOSED

- record PASS in `EVIDENCE_LEDGER`;
- remove blocker from `ACTIVE_WORK`;
- remove completed acceptance from `NEXT_WORK`;
- keep only product-level consequence in `CURRENT_STATE`;
- add `HISTORY` only for a meaningful milestone;
- release-facing result remains in release notes.

### BASELINE PASS -> REVALIDATION REQUIRED

A PASS is scoped to the tested behavior/build. Relevant code changes can make that evidence insufficient for the newest build without making the historical PASS false.

When a change touches a previously accepted behavior:

```text
old PASS remains historical baseline
        +
new REVALIDATION REQUIRED row
        -> current-build smoke/acceptance
        -> new PASS or FAIL
```

Examples:

- refactoring RDP socket classification requires revalidation of Hermes/direct counters;
- restructuring the 3-second agent loop requires a targeted OFF/ON smoke;
- changing SSH process detection requires a one-process/no-duplicate smoke.

Do not blindly inherit old PASS onto new code and do not re-run unrelated acceptance.

### SUPERSEDED

A fact/decision is superseded when newer architecture/implementation makes it non-current.

- remove obsolete detail from HOT files;
- never keep two contradictory current descriptions;
- if rationale matters, archive or rely on Git history;
- a durable old decision may keep a short tombstone (`SUPERSEDED by ...`) until compaction;
- historical evidence is preserved as historical truth, not rewritten away.

### ARCHIVED

Historical snapshots under `context/archive/` should state:

```text
Status: HISTORICAL / SUPERSEDED
Captured: YYYY-MM-DD
Superseded by: <current file / release / decision>
Reason retained: <why useful>
```

Archive is outside default context loading.

## Rewrite/delete vs explicit archive

### Remove from active context

Safe when no longer current/useful:

- old PR head after workstream changed;
- completed TODOs;
- obsolete next-step instructions;
- disproven hypotheses;
- temporary diagnostic commands;
- old UI mock text replaced by reality;
- repeated descriptions of the same PASS;
- stale `LAST_SESSION` detail already promoted elsewhere.

Git history retains the old version.

### Archive explicitly

Use archive for high-value history:

- deep product/architecture audits;
- major migration reasoning;
- release acceptance/evidence snapshots;
- superseded architecture rationale likely to matter later;
- incident/root-cause reports worth preserving.

Do not archive routine debugging noise.

## Evidence-ledger growth strategy

At a stable release/major milestone:

1. freeze release evidence, e.g. `context/archive/releases/v1.2.0-evidence.md`;
2. preserve evidence IDs/boundaries in that snapshot;
3. compact active ledger to current product guarantees + unresolved bugs + current-cycle acceptance;
4. reference archived release evidence rather than duplicating low-level rows forever;
5. if later code touches an old guarantee, create a new revalidation row.

## Decision growth strategy

`DECISIONS.md` contains currently applicable durable decisions, not every historical opinion.

When a decision changes:

1. add new decision/reason;
2. mark incompatible old decision `SUPERSEDED` with successor/date;
3. after stabilization, archive old detailed rationale only if valuable;
4. use Git history for ordinary old wording.

## Audit rotation

`LATEST_AUDIT.md` means one current deep audit.

When replaced:

- archive old audit if valuable;
- replace `LATEST_AUDIT` instead of appending generations;
- never let old audit TODOs participate in current default reading.

If no current audit is needed, a compact pointer is valid.

## LAST_SESSION lifecycle

`LAST_SESSION.md` is disposable:

- only latest intentional boundary delta;
- compact after facts are promoted into HOT/WARM files;
- do not archive every session;
- archive only unusually valuable unique reasoning.

## Soft size budgets

Crossing a budget triggers review/compaction before more context is added.

| File | Soft budget |
|---|---:|
| `README.md` | ~200 lines |
| `ACTIVE_WORK.md` | ~200 lines |
| `CURRENT_STATE.md` | ~350 lines |
| `NEXT_WORK.md` | ~300 lines |
| `PROJECT_HANDOFF.md` | ~250 lines |
| `DECISIONS.md` | ~300 lines |
| `EVIDENCE_LEDGER.md` | ~400 lines before release rotation |
| `LATEST_AUDIT.md` | ~500 lines |
| `LAST_SESSION.md` | ~150 lines |

Size is only a signal. A short stale file is still wrong; a temporarily larger truly active file can be acceptable after review.

## Compaction triggers

Compact when:

- release published;
- major PR/workstream merged/closed/abandoned;
- architecture changes;
- HOT/WARM file exceeds budget;
- completed TODOs/obsolete branch state remain;
- current files contradict each other;
- `LATEST_AUDIT` is no longer latest;
- evidence is hard to scan;
- project phase changes.

Compaction is normal maintenance, not data loss.

## Concurrent writer safety

Multiple chats/tools may touch context. Never assume the file SHA/content seen earlier is still current.

Before replacing an existing context file:

1. fetch the latest version/blob SHA;
2. compare with the version used to prepare the edit;
3. if it changed, **reconcile both changes**;
4. never force-overwrite a newer context checkpoint just to make the write succeed.

A GitHub SHA/409 conflict is a safety signal, not an inconvenience to bypass.

If two chats intentionally work in parallel, each must preserve the other chat's durable facts before writing a combined current state.

## Atomic checkpoint / commit-noise rule

One meaningful context checkpoint may touch several files (`ACTIVE_WORK`, evidence, state, roadmap). Prefer **one multi-file context commit per work-unit** where tooling allows it.

Do not create a separate commit for every file merely because several files need the same checkpoint.

Benefits:

- less noisy history;
- fewer default-branch commits;
- smaller feature-branch base drift;
- all related state transitions remain atomic in Git history.

If tooling only supports one-file commits, keep the group small and finish the complete checkpoint before unrelated engineering continues.

## Open PR / default-branch drift rule

Context-only commits may live on `main` while product code remains in a PR, but this makes the feature branch fall behind its base.

Rules:

- keep context-only changes disjoint from product PR files whenever practical;
- do not edit the same context files independently on `main` and the feature branch;
- before product merge, synchronize/rebase/merge current `main` into the feature branch as appropriate;
- resolve actual conflicts deliberately;
- rerun CI after reconciliation;
- recheck PR mergeability;
- do not interpret “branch behind” alone as a product regression.

If continuous context begins creating excessive base drift, reduce commit frequency by batching **work-units**, not by delaying persistence until end-of-chat.

## Context health audit

At milestones/releases and whenever something feels inconsistent, ask:

1. Can a new chat identify current stage in under two minutes?
2. Does `ACTIVE_WORK` match GitHub/deployment truth?
3. Are resolved blockers gone?
4. Does `NEXT_WORK` contain only remaining work?
5. Does `CURRENT_STATE` agree with evidence?
6. Are old PASSes scoped correctly after relevant code changes?
7. Are mutable refs distinguished from durable facts?
8. Are release notes evidence-backed?
9. Are superseded decisions retired?
10. Is historical detail outside default loading?
11. Are HOT files reasonably compact/repetition-free?
12. Would losing the current chat now still be safe?
13. Are secrets/sensitive production values absent?
14. Has any parallel writer produced a newer context version that must be reconciled?

Fix context before accumulating another large work-unit if any answer is no.

## Release-boundary garbage collection

At `vX.Y.Z`:

```text
freeze evidence -> archive/releases/vX.Y.Z-evidence.md
finalize release notes
compact ACTIVE_WORK for next cycle
compact EVIDENCE_LEDGER to baseline + open acceptance
rewrite CURRENT_STATE to released truth
remove completed NEXT_WORK
retire superseded decisions
archive obsolete deep audit
append one HISTORY milestone
compact LAST_SESSION
```

Start the next release with a small accurate working set.

## Git history is part of memory

Do not keep stale active text because deleting feels like losing information. Context commits are versioned. `archive/` is only for high-value historical snapshots.

## Anti-patterns

Do not:

- append forever;
- retain completed TODOs “for history”;
- leave a fixed bug as current blocker;
- duplicate branch/head/deployment detail in many files;
- archive every command/session;
- maintain multiple audits in `LATEST_AUDIT`;
- keep contradictory active decisions;
- apply an old PASS automatically to changed code;
- overwrite newer context from another writer;
- generate dozens of one-file commits for one logical checkpoint when batching is possible;
- use age alone to judge staleness.

## Freshness is semantic, not chronological

A fact is stale when it no longer describes current truth/work, not merely because it is old.

- `OpenSSH replaced FRP` may stay current for years.
- an active PR SHA can be stale after one commit.
- an old PASS remains real baseline evidence but may need revalidation after relevant changes.
- a fixed bug becomes historical after live acceptance.

This distinction is required for reliable long-term project memory.