# Hermes RDP vX.Y.Z — <release title>

Release: https://github.com/bakunity/RDP/releases/tag/vX.Y.Z

Short paragraph: what this release is for, why it exists, and whether it is a normal feature/stabilization release or a hotfix.

## Scope / headline

- major product change;
- major reliability/recovery change;
- major compatibility change;
- major security/lifecycle change;
- major UX/documentation change.

## Added

Describe new product capabilities. Prefer concrete behavior over generic phrases.

## Changed

Describe meaningful architecture, lifecycle, UX or operational changes.

## Fixed — bugs/root causes

For important bugs include:

- observed symptom;
- confirmed root cause;
- correction;
- bounded validation proving the correction.

Do not hide significant engineering work behind a single `bug fixes` bullet.

## Reliability / recovery

Record reboot, reconnect, failure-isolation, rollback, retry, timeout and lifecycle behavior relevant to this release.

## Compatibility

Record supported Windows/Linux variants, PowerShell constraints, migration behavior and any compatibility bugs fixed.

## Security

Record trust boundaries, credential/key handling, ACL/auth changes and Defender/security-tool coexistence. Do not expose secrets.

## Performance

Record meaningful performance regressions/fixes and evidence when available.

## Telegram / UI

Record control-state and UX changes that users will notice.

## Documentation / website

Record substantial documentation, public site and operator-guide updates.

## Validation / evidence

List the most important actual PASS scenarios for this exact release boundary:

- CI / release checks;
- real install/update/repair paths;
- real reboot/reconnect/failure tests;
- real user-facing RDP tests;
- regression suites added.

Link to `docs/VALIDATED_SCENARIOS.md` and/or durable context evidence where appropriate.

## Known limitations / deferred observations

Keep unresolved or intentionally deferred items explicit. Do not silently drop them from the release record.

## Breaking changes / migration

State breaking changes clearly. If none, say so.

## Recommendation

State whether this is the recommended version and whether an older tag should be avoided for a known reason.
