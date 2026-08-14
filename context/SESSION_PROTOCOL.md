# Hermes RDP — Continuous Context Protocol

Updated: 2026-08-08

Purpose: make the project recoverable from GitHub at any moment even if the current chat is compressed, lost or abandoned, while also preventing context from becoming a stale append-only dump.

## Principle

```text
chat = temporary working memory
runtime / CI = evidence
HOT context = current durable working memory
archive / Git history = historical memory
```

Context is both **continuously checkpointed** and **continuously compacted**.

Saving a fact and retiring an obsolete fact are equally important operations.

## Start of every project chat

Read in this order:

1. `context/README.md`;
2. `context/ACTIVE_WORK.md`;
3. `context/EVIDENCE_LEDGER.md`;
4. `context/CURRENT_STATE.md`;
5. `context/PROJECT_HANDOFF.md`;
6. `context/NEXT_WORK.md`;
7. `context/DECISIONS.md`;
8. `context/SESSION_PROTOCOL.md` / `CONTEXT_LIFECYCLE.md` if changing project-memory rules;
9. `LATEST_AUDIT`, `LAST_SESSION` and archive only when deeper/history context is needed;
10. inspect current GitHub PRs/branches/releases/files before acting.

Establish explicitly:

- what is actually deployed;
- active PR/branch/head;
- latest real PASS/FAIL;
- implemented-but-not-runtime-validated changes;
- confirmed current blockers;
- exact next action.

Do not repeat an old PASS unless a relevant change can regress it.

## During work — checkpoint by work-unit

A work-unit is a meaningful state transition:

```text
diagnosis -> confirmed root cause
code -> CI green
deploy -> live state changed
acceptance -> PASS/FAIL
fix -> runtime accepted
decision -> durable constraint changed
stage -> next stage changed
```

Do not wait for chat migration.

### Immediate checkpoint triggers

#### Live PASS / FAIL

- update `EVIDENCE_LEDGER.md`;
- update `ACTIVE_WORK.md` if the result changes current work;
- update `CURRENT_STATE.md` when product-level truth changed;
- remove the accepted blocker from `NEXT_WORK.md` when its whole acceptance item is complete.

#### Confirmed bug / root cause

- add durable evidence to `EVIDENCE_LEDGER.md`;
- keep it in `ACTIVE_WORK.md` while it blocks current work;
- do not record a guess as confirmed.

#### Code + CI completes a meaningful fix

- update `ACTIVE_WORK.md` with current branch/head and `IMPLEMENTED, NOT VALIDATED` where runtime acceptance is still needed;
- update release draft if release-facing;
- CI does not promote environment-dependent behavior to runtime PASS.

#### Deployment changes live truth

- update `ACTIVE_WORK.md` with deployed vs branch-only state;
- record rollback/backup point when useful;
- do not equate branch head with deployed head without evidence.

#### Durable decision

- update `DECISIONS.md` immediately;
- retire/supersede the incompatible old decision;
- update `PROJECT_HANDOFF.md` only when product/architecture understanding materially changed.

#### Acceptance queue changes

- rewrite `NEXT_WORK.md` to remove completed stages and reorder remaining work;
- do not keep completed TODOs for historical purposes.

## Safety checkpoint rule

Do not let many meaningful changes exist only in chat.

If several work-units happen close together, combine them into one compact checkpoint. Losing the last 10–20 chat messages should not erase an important project-state transition.

Record outcomes, not command transcripts.

## Continuous stale-context retirement

After updating new truth, check whether the new truth makes old context stale.

Examples:

- a bug becomes live-accepted -> remove it from `ACTIVE_WORK` and remaining TODOs;
- a new PR replaces an old workstream -> remove old branch/head from HOT files;
- endpoint CLOSED becomes measured PASS -> remove old “not separately proven” wording from current files;
- an architecture decision changes -> mark the old decision `SUPERSEDED`, do not leave both active;
- a newer deep audit exists -> archive the old audit instead of stacking both in `LATEST_AUDIT`.

See `CONTEXT_LIFECYCLE.md` for lifecycle, archive and size rules.

## Canonical-owner rule

Before adding detailed text, ask: **which file owns this fact?**

- operational truth -> `ACTIVE_WORK`;
- evidence -> `EVIDENCE_LEDGER`;
- consolidated state -> `CURRENT_STATE`;
- architecture -> `PROJECT_HANDOFF`;
- remaining work -> `NEXT_WORK`;
- durable choice -> `DECISIONS`;
- release-facing result -> release draft;
- historical reasoning -> archive.

Other files should summarize/link instead of carrying another independently maintained copy.

## File-specific behavior

### `ACTIVE_WORK.md`

Frequently rewritten. Contains only current work:

- active PR/head/release target;
- deployment truth/rollback point;
- current blockers;
- implemented-not-accepted work;
- exact next action;
- baseline checks that should not be repeated.

Remove completed blockers promptly.

### `EVIDENCE_LEDGER.md`

Durable evidence index. Preserve historical PASS/bug evidence, but rotate/compact by release as defined in `CONTEXT_LIFECYCLE.md`.

Never rewrite an old failure as if it never happened; add resolution/new acceptance.

### `CURRENT_STATE.md`

Consolidated current product truth. Rewrite when materially stale. It must not carry old TODO/status just because the text once existed.

### `PROJECT_HANDOFF.md`

Stable architecture/product model. Avoid exact temporary PR/acceptance detail unless needed to understand architecture.

### `NEXT_WORK.md`

Only remaining work. Completed items move out; history/release notes preserve what was done.

### `DECISIONS.md`

Only currently applicable durable decisions plus short supersession tombstones when necessary. Old incompatible rationale goes to history/archive/Git.

### `LATEST_AUDIT.md`

Exactly one current deep audit. Archive/replace when superseded. It is allowed to be a short pointer if no new deep audit is needed.

### `LAST_SESSION.md`

Optional disposable chat-boundary delta. Never primary truth. Compact it after its facts are promoted into HOT/WARM files.

### `HISTORY.md`

Major milestones only. Do not log every PR commit or acceptance command.

## Context health / garbage collection triggers

Run a compact health review when:

- a release is published;
- a major PR/workstream closes;
- project phase changes;
- HOT/WARM file exceeds its soft budget;
- two current files contradict each other;
- old blockers/TODOs are visibly lingering;
- active evidence becomes hard to scan;
- `LATEST_AUDIT` is no longer latest.

Health review questions:

1. Can a new chat identify the exact next step quickly?
2. Does `ACTIVE_WORK` match actual GitHub/deployment truth?
3. Are resolved bugs removed from current blockers?
4. Does `NEXT_WORK` contain only remaining work?
5. Does `CURRENT_STATE` agree with `EVIDENCE_LEDGER`?
6. Are superseded decisions retired?
7. Are release claims evidence-backed?
8. Is historical detail outside the default reading path?
9. Would losing this chat now still be safe?
10. Are secrets absent?

## Release boundary protocol

At `vX.Y.Z`:

1. freeze relevant evidence to `context/archive/releases/vX.Y.Z-evidence.md`;
2. finalize release notes from evidence + release draft;
3. compact `EVIDENCE_LEDGER` to current guarantees + open next-cycle acceptance;
4. rewrite `CURRENT_STATE` to released truth;
5. reset `ACTIVE_WORK` for the next workstream;
6. remove completed items from `NEXT_WORK`;
7. retire superseded decisions;
8. archive obsolete deep audit;
9. append one meaningful `HISTORY` milestone;
10. compact/replace `LAST_SESSION` if needed.

The next release cycle should start with a small accurate working set.

## Before risky live changes

Before a deploy/migration/update that could break access, ensure `ACTIVE_WORK.md` contains enough recovery state:

- current live state;
- what is about to change;
- known rollback/backup point when useful;
- exact acceptance target.

Never put secrets into context.

## Before intentionally moving chat

A final handoff is still useful, but it is consolidation, not the first persistence point:

- ensure HOT context is current;
- compact stale material;
- refresh `CURRENT_STATE/NEXT_WORK` as needed;
- update decisions/history/release notes only where appropriate;
- optionally rewrite `LAST_SESSION` with a very short delta.

If the chat disappears before this, continuous checkpoints must still be sufficient.

## Evidence vocabulary

Use consistently:

- **PASS / CONFIRMED** — real evidence exists;
- **IMPLEMENTED, NOT VALIDATED** — code exists, runtime acceptance absent;
- **FAIL / CONFIRMED BUG** — reproduced/established failure;
- **HYPOTHESIS / LIKELY** — suspected, not proven;
- **PLANNED** — not implemented;
- **SUPERSEDED** — historically true/accepted text that no longer describes current truth.

## Sensitive information

Never store passwords, bot tokens, private keys, device tokens, pairing codes, secret configs/fingerprints, unnecessary production IPs, numeric personal IDs or secret-bearing logs.

## Interaction conventions

- Russian;
- one live infrastructure stage at a time;
- whole copy-paste commands;
- avoid manual nano/vim when unnecessary;
- explicit PASS/FAIL from output;
- rollback plan where practical;
- do not weaken Defender;
- do not reintroduce FRP casually;
- finish coherent behavior before cosmetic expansion.