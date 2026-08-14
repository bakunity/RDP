# Hermes RDP — Latest Audit Pointer

Updated: 2026-08-14

The full historical product audit remains in:

`context/archive/2026-08-07-full-product-audit.md`

Do not treat that archive as the current execution plan. For current truth use:

1. `ACTIVE_WORK.md`
2. `CURRENT_STATE.md`
3. `NEXT_WORK.md`
4. `EVIDENCE_LEDGER.md`

Current major delta since the archived audit:

- trusted public-IP Windows RDP certificate lifecycle is bounded live-accepted through CERT-012;
- CERT-013 normal Windows lifecycle integration completed all live product gates on accepted product/test code head `e11cf89ed26d551ca92b4010034d6e6792a9266b`;
- CI #381 passed Linux full release checks + Windows PowerShell 5.1;
- accepted CERT-013 paths: transactional Update, targeted Repair, clean Fresh Install on disposable Win10 fixture, real external trusted Microsoft RDP, normal Uninstall;
- release-note process now uses rolling `docs/releases/UNRELEASED.md`, compact public version notes and separate long-form history files.

Natural renewal-driven certificate thumbprint rotation remains a deferred real-world observation and is not a blocker.
