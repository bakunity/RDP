# Hermes RDP — Continuous Context Protocol

Purpose: make the project recoverable from GitHub at any moment, even if the current chat is compressed, partially lost or abandoned before a planned handoff.

## Principle

Do not treat the conversation as the source of truth.

```text
chat = temporary working memory
GitHub context = durable project memory
runtime/CI = evidence
```

The context system is **event-driven**. Important facts are checkpointed when they become durable, not only at the end of a conversation.

## At the beginning of every project chat

Read in this order:

1. `context/README.md`;
2. `context/ACTIVE_WORK.md`;
3. `context/EVIDENCE_LEDGER.md`;
4. `context/CURRENT_STATE.md`;
5. `context/PROJECT_HANDOFF.md`;
6. `context/NEXT_WORK.md`;
7. `context/DECISIONS.md`;
8. `context/LATEST_AUDIT.md` if deeper reasoning is needed;
9. `context/LAST_SESSION.md` only as a chat-boundary delta;
10. inspect current GitHub PRs/branches/releases/files before acting.

Then briefly establish:

- what is actually deployed;
- active PR/branch/head;
- latest real PASS/FAIL;
- implemented-but-not-live-validated changes;
- confirmed bugs;
- exact next engineering action.

Do not automatically repeat an acceptance scenario already recorded as PASS unless a relevant change could have regressed it.

## During the chat: checkpoint after work-units

A **work-unit** is a meaningful state transition, for example:

- diagnosis -> confirmed root cause;
- code change -> CI green;
- deploy -> services healthy;
- live test -> PASS/FAIL;
- bug fix -> runtime accepted;
- product/architecture choice -> durable decision;
- current stage -> next stage.

After a completed work-unit, update the appropriate durable files before a large amount of new work accumulates in chat.

### Mandatory immediate checkpoint triggers

Checkpoint without waiting for session end when any of these occurs:

1. **Live PASS/FAIL**
   - update `EVIDENCE_LEDGER.md`;
   - update `ACTIVE_WORK.md` if it changes current stage;
   - update `CURRENT_STATE.md` when product-level status changes.

2. **Confirmed bug/root cause**
   - record it in `EVIDENCE_LEDGER.md`;
   - add it to `ACTIVE_WORK.md` until fixed/accepted;
   - do not record an unproven guess as confirmed.

3. **Code + CI completes a meaningful fix**
   - update `ACTIVE_WORK.md` with head/status;
   - label it `IMPLEMENTED, NOT VALIDATED` until runtime acceptance if behavior is environment-dependent;
   - update active release draft if user-facing/release-relevant.

4. **Deployment changes live truth**
   - update `ACTIVE_WORK.md` with what is actually deployed and rollback point if useful;
   - do not equate branch head with deployed head without evidence.

5. **Durable decision**
   - update `DECISIONS.md` immediately;
   - update `PROJECT_HANDOFF.md` only if the architecture/product vector materially changed.

6. **Acceptance queue changes**
   - update `NEXT_WORK.md` when priorities/stages materially change;
   - remove completed items rather than leaving stale TODOs indefinitely.

### Safety checkpoint rule

Do not let many meaningful changes exist only in chat.

If several work-units happen close together, combine them into one compact checkpoint. The goal is not to commit after every command; the goal is to ensure that losing the last 10–20 messages would not erase important project truth.

Good checkpoint:

```text
- endpoint false-positive root cause confirmed
- server-side listener truth implemented + CI PASS
- deployed + OFF=CLOSED / ON=OPEN live PASS
- next: RDP channel split
```

Bad checkpoint:

```text
- ran command A
- copied file B
- clicked refresh
- typo happened
```

## File responsibilities

### `ACTIVE_WORK.md` — hot operational state

Rewrite frequently. It should answer in under a minute:

- active PR/branch/head;
- release target;
- what is deployed;
- current confirmed blockers;
- what is implemented but not accepted;
- exact next step;
- what must not be repeated.

This is the main protection against chat compression.

### `EVIDENCE_LEDGER.md` — durable proof index

Update immediately after acceptance/root-cause events.

Each entry should preserve:

- scenario;
- status;
- evidence boundary;
- relevant environment/build when needed.

Never promote CI-only evidence to runtime PASS.

### `CURRENT_STATE.md` — consolidated product truth

Rewrite when enough state changes that the snapshot becomes materially stale.

It should not need updating after every small commit, but it must not remain weeks behind while `ACTIVE_WORK` has moved on.

### `PROJECT_HANDOFF.md` — architecture/product vector

Update only for meaningful architectural/product understanding changes.

### `NEXT_WORK.md` — active roadmap / acceptance queue

Update when stages complete, new blockers appear or priorities change.

### `DECISIONS.md` — durable constraints

Update as soon as a decision future chats must not casually reverse is accepted.

Do not put temporary debugging hypotheses here.

### `HISTORY.md` — major milestones

Append only significant milestones. Not a work log.

### `LAST_SESSION.md` — optional boundary delta

Still useful when intentionally pausing/moving chats, but it is **not** the primary operational memory anymore.

A chat may disappear without a clean `LAST_SESSION` update; `ACTIVE_WORK + EVIDENCE_LEDGER + CURRENT_STATE` must still be enough to continue.

### Release draft

During an active stabilization/release cycle, maintain a draft under `docs/releases/`.

Only move items to the confirmed section when evidence supports them. Keep `IMPLEMENTED, NOT VALIDATED` separate.

## Branch policy for context

Product code changes normally live in feature branches/PRs.

Context-only checkpoint commits may go directly to default `main` even while product PRs are open. This is intentional because default-branch context must describe unmerged active work for future chats.

Rules:

- context-only commits must not silently alter product runtime;
- refer to open PR/branch/head explicitly;
- distinguish deployed vs branch-only state;
- never claim an unmerged fix is production simply because context on `main` mentions it.

Recommended commit prefixes:

```text
context: checkpoint <milestone>
context: record <confirmed bug/pass>
context: update active work after <event>
```

## Evidence language

Use consistently:

- **PASS / CONFIRMED** — real evidence exists;
- **IMPLEMENTED, NOT VALIDATED** — code exists, runtime acceptance absent;
- **FAIL / CONFIRMED BUG** — reproduced/established failure;
- **HYPOTHESIS / LIKELY** — suspected but not proven;
- **PLANNED** — not implemented.

When a fix may invalidate an older PASS, preserve the baseline evidence and create a fresh acceptance requirement for the new build.

## Before risky live changes

Before a deploy/migration/update that could break access, make sure `ACTIVE_WORK.md` contains enough information to recover:

- current live state;
- what is about to change;
- known rollback/backup point when available;
- exact acceptance target.

Do not put secrets into the checkpoint.

## Before intentionally moving to another chat

A final handoff is still useful, but now it is a **consolidation**, not the first time facts are saved.

1. ensure `ACTIVE_WORK.md` is current;
2. ensure new live evidence is in `EVIDENCE_LEDGER.md`;
3. rewrite stale parts of `CURRENT_STATE.md`;
4. refresh `NEXT_WORK.md`;
5. update `DECISIONS.md` / `PROJECT_HANDOFF.md` only if needed;
6. append `HISTORY.md` for a meaningful milestone;
7. rewrite `LAST_SESSION.md` as a compact delta if useful;
8. update release draft/final notes.

If the chat disappears before this step, the project must still be recoverable from the continuous checkpoints.

## Sensitive information policy

Never write into public context:

- passwords;
- bot tokens;
- private keys;
- device tokens;
- pairing codes;
- secret-bearing fingerprints/configs;
- unnecessary production IPs;
- personal numeric Telegram IDs;
- full secret logs.

## Interaction conventions worth preserving

- Russian;
- one live infrastructure stage at a time;
- copy-paste commands;
- avoid manual nano/vim when a command can do the work;
- explicit PASS/FAIL after output;
- rollback plan where practical;
- do not weaken Defender;
- do not reintroduce FRP casually;
- finish coherent product behavior before cosmetic expansion.