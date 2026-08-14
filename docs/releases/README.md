# Hermes RDP release notes

This directory is the **long-form source of truth for every Hermes RDP release**.

GitHub Release descriptions must be generated/synchronized from the matching file here. The short `CHANGELOG.md` remains a compact index; detailed engineering history, bugs found, acceptance evidence and compatibility notes belong in these versioned release files.

## Files

- `UNRELEASED.md` — rolling ledger for work completed or discovered after the latest published release.
- `_TEMPLATE.md` — structure for a future version file.
- `vX.Y.Z.md` — frozen long-form notes for a published release.

## Working rule

Do not wait until release day to reconstruct the release from memory.

Whenever meaningful product work is completed, a bug/root cause is confirmed, a live acceptance becomes PASS, compatibility changes, documentation is substantially updated, or a release blocker is discovered, update `UNRELEASED.md` in the same development cycle.

The rolling file should distinguish:

- merged/shipped candidate work;
- in-progress work that is **not yet release-ready**;
- bugs found and their resolution status;
- live validation / CI evidence;
- security and compatibility changes;
- documentation changes;
- known limitations / deferred observations;
- breaking changes or migrations.

Never convert an untested requirement into a release PASS merely because code exists.

## Preparing a release

1. Review `UNRELEASED.md` against `context/EVIDENCE_LEDGER.md`, merged PRs and current CI.
2. Create `docs/releases/vX.Y.Z.md` from `_TEMPLATE.md` and move/curate all relevant facts from `UNRELEASED.md`.
3. Keep the version file detailed. Do not compress weeks of stabilization into a few generic bullets.
4. Update `CHANGELOG.md` with the concise version summary.
5. Update `VERSION`, package metadata and release documentation in the final validated release tree.
6. Run full release checks.
7. Publish only from the validated workflow HEAD.
8. After publication, verify that the GitHub Release body exactly reflects `docs/releases/vX.Y.Z.md`.
9. Reset `UNRELEASED.md` to the new base release while preserving any work that was not shipped.

## Historical release notes

Published `vX.Y.Z.md` files are durable product history. They may be corrected or expanded when an old description omitted factual work, but:

- never rewrite an existing Git tag;
- clearly document historical packaging/tag defects;
- do not retroactively claim functionality that was implemented only after that tag/release tree;
- keep corrections grounded in tag content, changelog, PR/commit history and accepted evidence.

## GitHub Release synchronization

`.github/workflows/release.yml` treats the matching `docs/releases/vX.Y.Z.md` file as the release-body source of truth.

- new releases are created from that file;
- an existing current release is updated from that file;
- if an already-published historical `docs/releases/v*.md` changes, the corresponding existing GitHub Release body is synchronized without moving or rewriting its tag.

## Security / privacy

Release notes must never contain:

- pairing codes;
- API/device tokens;
- private keys or PFX material/passwords;
- real Telegram owner IDs;
- secret infrastructure credentials;
- other secret-bearing runtime data.

Public IPs, exact device IDs and other environment-specific values should only be included when they are intentionally public product facts and materially useful; prefer generic evidence descriptions otherwise.
