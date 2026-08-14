# Hermes RDP — Architectural Decisions

This file records currently applicable decisions that future chats should not casually reverse. Superseded decisions should be retired according to `CONTEXT_LIFECYCLE.md` rather than left as contradictory current guidance.

## Product / architecture

### 1. Only the Linux server is special

All Windows PCs are equal clients.

Do not introduce a “main PC” code path. Every Windows device should use the same installer, agent, pairing flow and control semantics.

### 2. OpenSSH replaced FRP in the active architecture

Reason: official FRP Windows binary triggered Microsoft Defender false-positive/quarantine problems and created a poor deployment experience.

Current design uses:

- Windows built-in `ssh.exe` / `ssh-keygen.exe`;
- isolated server `sshd`;
- per-device Ed25519 keys;
- per-device `permitlisten` restrictions.

Do not reintroduce FRP into the core runtime as a workaround without a deliberate architectural decision.

### 3. Do not weaken Defender

The product should work without Microsoft Defender exclusions or disabling protection.

### 4. Administrative SSH is independent

Hermes tunnel sshd must not replace or casually modify the server's normal administrative SSH on port 22.

### 5. Private SSH key stays on Windows

Server receives/stores only the public key.

### 6. Each device owns its identity

Per device:

- device ID;
- API token;
- Ed25519 public key;
- persistent RDP port;
- telemetry;
- command sequence/state.

Do not use a shared tunnel credential model for all Windows devices.

### 7. Endpoint isolation must be enforced server-side

A device key may only listen on its assigned endpoint. Current mechanism is OpenSSH `permitlisten` produced by `AuthorizedKeysCommand`.

### 8. Telegram is a control plane, not RDP transport

RDP traffic never flows through Telegram.

### 9. Agent ONLINE != RDP access enabled

The Windows agent should continue polling/heartbeating while access is OFF so it can receive an ON command.

Correct state can be:

```text
Agent ONLINE
Access OFF
SSH disconnected
Endpoint closed
```

### 10. Dashboard must show actual state, not only intent

A button press/queued command is not success.

Keep distinct:

- desired state;
- command lifecycle;
- actual SSH state;
- actual endpoint state;
- RDP sessions/channel.

### 11. One Telegram dashboard message

Preferred UX is to edit one dashboard message instead of sending a growing stream of status messages.

### 12. Pairing is security-sensitive and should be atomic

Do not consume a one-time code before prerequisites are ready. Failed client setup after pairing should revoke the created device where possible.

### 13. Stable installs use immutable refs

Production install/update documentation should use a published release tag or known immutable commit, not mutable `main`.

### 14. Published tags are immutable

Do not move/overwrite a published release tag. Critical corrections become a new patch version.

## Windows installer / operations

### 15. No manual editor workflow

Prefer complete copy-paste PowerShell/Bash commands rather than asking the operator to edit files in nano/vim.

### 16. Preserve old installation before destructive migration

Legacy migration should create a recoverable backup/archive before new pairing.

### 17. Legacy backup should not recursively read protected old keys

Preferred migration is same-volume directory rename/move. Use scoped ACL takeover only as fallback.

### 18. Update must have a rollback story

A backup alone is not enough. Target design validates the new runtime and restores the previous working version on failed update where practical.

## Security / privacy

### 19. Never put secrets in repository context/docs

Do not store or echo:

- Telegram bot token;
- numeric owner IDs when not required;
- pairing codes;
- API/TLS fingerprints in ready-to-use secret commands;
- private SSH keys;
- device tokens;
- production secret configs;
- real production public IPs in public examples when unnecessary.

### 20. RDP endpoint remains a Windows security boundary

Hermes secures registration/tunnel/control but does not replace Windows RDP security. NLA, strong credentials, updates and sensible network policy remain relevant.

### 29. Trusted RDP certificate track targets the public IP first

Do not introduce a domain solely to make the endpoint look nicer. The user chose to proceed with a publicly trusted certificate for the existing public IP if issuance and renewal are practical.

Important boundary:

- HTTPS/API TLS and Windows RDP listener TLS are separate;
- adding a domain alone does not remove the Microsoft Remote Desktop certificate warning;
- the certificate presented by the **Windows RDP listener** must match the address used by the RDP client;
- domain-based design may be revisited only if public-IP certificate issuance/renewal proves unsuitable or if it provides a concrete product benefit.

First acceptance must be on a non-critical Windows fixture with rollback to the previous listener certificate/state.

## Documentation / product presentation

### 21. Documentation must explain architecture visually

Use useful diagrams, arrows, Mermaid flows and explicit lifecycle explanations. Sparse component lists are not finished documentation.

### 22. Old v1.0.7 docs are a structural reference only

Reuse clarity/organization, not obsolete FRP implementation details.

### 23. Website explains product before technology

Lead with:

```text
multiple Windows PCs -> one Hermes server -> remote RDP access
                               |
                               -> Telegram control
```

Then explain OpenSSH/Ed25519/pinning.

### 24. Do not fake product status in marketing UI

Website/dashboard mockups should match actual supported behavior and terminology.

## Development workflow

### 25. Verify before claiming PASS

Infrastructure/runtime stages are accepted only after observable output/result. CI and source inspection have narrower evidence boundaries.

### 26. Work in small logical PRs

Preferred stabilization sequence:

1. correctness;
2. reliability;
3. Telegram UX;
4. docs/README;
5. website;
6. acceptance/release.

Do not combine unrelated refactors into one risky change.

### 27. Project context is continuous, not end-of-chat only

Do not rely on `LAST_SESSION.md` or the current chat retaining intermediate facts.

Durable project memory is event-driven:

- `ACTIVE_WORK.md` = hot operational checkpoint;
- `EVIDENCE_LEDGER.md` = PASS/FAIL/root-cause/revalidation evidence;
- `CURRENT_STATE.md` = consolidated product snapshot;
- release-facing changes are accumulated during development, not reconstructed from memory afterward.

Context-only checkpoints may go directly to `main` while product code remains in a feature PR so a new chat can recover active work from the default branch.

Checkpoint after meaningful work-units, not every command. When several context files change for one work-unit, prefer one batched multi-file commit where tooling permits. Before product merge, reconcile the feature branch with current `main` and rerun CI.

### 28. Project context is lifecycle-managed, not append-only

Saving facts is not enough. Active memory must actively retire stale information.

Rules:

- HOT files describe current truth/work, not history;
- completed TODOs leave `NEXT_WORK`;
- fixed blockers leave `ACTIVE_WORK` after acceptance;
- old PASS remains historical evidence but relevant code changes create an explicit `REVALIDATION REQUIRED` obligation;
- superseded architecture/decisions are not left beside their replacements as if both were current;
- high-value obsolete reasoning moves to archive, while ordinary previous wording relies on Git history;
- `LATEST_AUDIT` contains one current audit only;
- `LAST_SESSION` is disposable and non-authoritative;
- soft size budgets trigger compaction;
- release boundaries trigger evidence/state garbage collection;
- before overwriting context, fetch latest file/SHA and reconcile concurrent changes rather than blindly replacing newer state.

The purpose is to keep project memory **small enough to read, complete enough to resume, and explicit about evidence scope**.
