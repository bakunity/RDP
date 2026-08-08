# Hermes RDP — Architectural Decisions

This file records decisions that future chats should not casually reverse.

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

This is critical.

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

Need distinction between:

- desired state;
- command lifecycle;
- actual SSH state;
- actual endpoint state;
- RDP sessions.

### 11. One Telegram dashboard message

The preferred UX is to edit one dashboard message instead of sending a growing stream of status messages.

### 12. Pairing is security-sensitive and should be atomic

Do not consume a one-time code before prerequisites are ready. Failed client setup after pairing should revoke the created device where possible.

### 13. Stable installs use immutable refs

Production install/update documentation should use a published release tag or a known immutable commit, not mutable `main`.

### 14. Published tags are immutable

Do not move/overwrite a published release tag. Critical corrections become a new patch version.

## Windows installer / operations

### 15. No manual editor workflow

For operator instructions, prefer complete copy-paste PowerShell/Bash commands rather than asking the user to edit files in nano/vim.

### 16. Preserve old installation before destructive migration

Legacy migration should create a recoverable backup/archive before new pairing.

### 17. Legacy backup should not recursively read protected old keys

Preferred migration behavior is same-volume directory rename/move. Use scoped ACL takeover only as fallback.

### 18. Update must have a rollback story

A backup alone is not enough. Target design should validate the new runtime and automatically restore the previous working version on failure.

## Security / privacy

### 19. Never put secrets in repository context/docs

Do not store or echo:

- Telegram bot token;
- numeric owner IDs when not required;
- pairing codes;
- API/TLS fingerprints in a ready-to-use command;
- private SSH keys;
- device tokens;
- production secret configs;
- real production public IPs in public examples.

### 20. RDP endpoint remains a Windows security boundary

Hermes secures registration/tunnel/control but does not replace Windows RDP security. NLA, strong credentials, Windows updates and sensible network policy remain relevant.

## Documentation / product presentation

### 21. Documentation must explain architecture visually

The user strongly prefers useful diagrams, arrows, Mermaid flows and explicit lifecycle explanations. Sparse files that merely list components are not considered finished documentation.

### 22. Old v1.0.7 docs are a structural reference only

Reuse their clarity and organization, but do not copy obsolete FRP implementation details into OpenSSH docs.

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

During infrastructure work, each stage is accepted only after observable output/result.

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

Do not rely on `LAST_SESSION.md` or the current chat retaining all intermediate facts.

Durable project memory is event-driven:

- `ACTIVE_WORK.md` stores the hot operational checkpoint;
- `EVIDENCE_LEDGER.md` stores live PASS/FAIL and confirmed root causes;
- `CURRENT_STATE.md` stores the consolidated product snapshot;
- release-facing changes are accumulated while the release is being built, not reconstructed afterward.

Context-only checkpoint commits may go directly to `main` while product code remains in a feature PR. This is intentional so a future chat can recover active work from the default branch even before the product PR is merged.

Checkpoint after meaningful work-units such as confirmed diagnosis, code+CI, deploy, live acceptance, durable decision or change of exact next target. Do not create a transcript of every command.