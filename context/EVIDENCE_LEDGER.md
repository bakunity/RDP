# Hermes RDP — Evidence Ledger

Updated: 2026-08-13

Operational evidence continues in `ACTIVE_WORK.md` and `CURRENT_STATE.md`.

## Stage 4 updater evidence

| ID | Scenario | Status | Evidence / boundary |
|---|---|---|---|
| UPD-001 | Server updater runtime/source baseline | PASS | Healthy immutable deployment baseline established. |
| UPD-002 | Legacy server update backup includes live DB | CONFIRMED BUG / RESOLVED | Legacy backup omitted SQLite state; PR #22 added consistent DB backup/provenance. |
| UPD-003 | Transactional server updater success path | PASS | Exact PR #22 head live update preserved device/DB state, created valid rollback anchor and recovered all active endpoints. |
| UPD-004 | Server automatic rollback after post-mutation fault | PASS | Forced failure produced `ROLLBACK=PASS`; ref/config/app/units/DB metadata/device state/services/health/endpoints restored. |
| UPD-005 | Transactional Windows updater success path | PASS | On `SEC005 TEST`, exact PR #23 updater returned `UPDATE=PASS`; device state and port preserved, task definition unchanged/Running, backup valid, one agent + one matching SSH, endpoint open. |

UPD-005 first invocation had an external in-memory harness BOM issue before product execution; it caused no runtime mutation and is classified HARNESS FAIL / NOT PRODUCT FAIL.

## Durable prior evidence

All earlier transport, Telegram control, compatibility, performance, lifecycle, security and PR acceptance evidence remains accepted as recorded in repository history. Do not re-run completed suites without a concrete regression reason. SEC-004 remains fixture-unavailable; RL-006 remains optional partial closure only.

## Current gate

UPD-006 bounded Windows forced-failure automatic rollback on `SEC005 TEST`. Do not merge PR #23 before that gate passes.

## Update rule

Record demonstrated PASS/FAIL/root-cause/deployment transitions only. Never store pairing codes, API tokens, private keys or ready-to-use secret material.
