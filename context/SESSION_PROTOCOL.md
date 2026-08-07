# Hermes RDP — Cross-Chat Session Protocol

Purpose: make long project work portable between ChatGPT conversations without relying on the old chat remaining available.

## At the beginning of every new project chat

The assistant should:

1. read `context/README.md`;
2. read `context/PROJECT_HANDOFF.md`;
3. read `context/CURRENT_STATE.md`;
4. read `context/NEXT_WORK.md`;
5. read `context/DECISIONS.md`;
6. inspect the relevant current GitHub files/PRs/releases before acting;
7. briefly tell the user what is understood and what stage is next;
8. do not silently assume the context snapshot is newer than GitHub.

Suggested user prompt:

> Открой `context/README.md` в `bakunity/RDP`, прочитай project handoff и продолжай с текущего состояния. Сначала сверь GitHub и ничего не меняй, пока не подтвердим следующий этап.

## During a session

The context files are not a substitute for normal engineering evidence.

For any live change:

- inspect current source first;
- use a branch/PR for product code changes unless there is a clear reason not to;
- run appropriate CI/tests;
- do not mark anything PASS only because the code looks correct;
- for infrastructure/recovery behavior, require actual runtime output or user confirmation.

## Before moving to another chat

Update the context **after** the useful work of the session is complete.

### Update `CURRENT_STATE.md`

Replace stale state with the latest facts:

- current release;
- current important `main` commit if useful;
- what was actually tested;
- which bugs remain;
- what is deployed;
- what is intentionally not deployed.

Do not leave an item under “not tested” after it has been confirmed.

### Update `PROJECT_HANDOFF.md`

Keep it compact but sufficient for a new engineer/chat to understand:

- architecture;
- why major decisions were made;
- latest important discoveries;
- current blockers;
- user expectations;
- next product direction.

Do not turn it into a raw transcript.

### Update `NEXT_WORK.md`

Remove completed stages and reorder priorities if the project direction changed.

### Update `DECISIONS.md`

Only when a durable architectural/product decision changed or a new durable constraint was accepted.

Do not add temporary debugging guesses as permanent decisions.

### Append to `HISTORY.md`

Add one dated entry for meaningful milestones such as:

- architecture migration;
- production deployment;
- critical bug discovery/fix;
- successful acceptance scenario;
- stable release;
- major documentation/site rebuild.

Keep entries concise.

## Evidence language

Use these terms consistently:

- **CONFIRMED / PASS** — actual test/output/user confirmation exists.
- **IMPLEMENTED, NOT VALIDATED** — code exists but runtime scenario was not proven.
- **LIKELY / HYPOTHESIS** — suspected root cause that still needs evidence.
- **PLANNED** — desired future work, no implementation claim.

This distinction is especially important for networking, recovery and ON/OFF behavior.

## Sensitive information policy

Never write into `context/`:

- passwords;
- bot tokens;
- private keys;
- device tokens;
- pairing codes;
- ready-to-use secret fingerprints;
- production IPs when unnecessary;
- personal numeric Telegram IDs;
- full secret-bearing logs.

Use placeholders such as:

```text
SERVER_IP_OR_DOMAIN
DEVICE_PORT
PAIR_CODE
TLS_FINGERPRINT
DEVICE_ID
```

## Interaction conventions to preserve

The user prefers:

- Russian;
- direct and practical engineering discussion;
- one live infrastructure stage at a time;
- commands that can be pasted whole;
- no manual nano/vim editing when a command can write the file;
- a rollback command/plan where practical;
- explicit checking of command output;
- strong architecture diagrams and explanatory documentation;
- a finished coherent product rather than a collection of partially polished features.

## What future chats should not do

- do not reintroduce FRP because it is familiar;
- do not disable Defender as an installation strategy;
- do not confuse `ONLINE` heartbeat with RDP access being ON;
- do not claim the SSH tunnel is stopped solely from the current unreliable telemetry field;
- do not treat “command sent” as “command completed”;
- do not redesign the website before core state correctness unless the user explicitly reprioritizes;
- do not overwrite published release tags;
- do not expose secrets while asking for diagnostics.

## Context commit convention

Recommended commit prefix:

```text
context: update project handoff after <milestone>
```

The context folder itself is project documentation and should stay readable in GitHub without tooling.