# Hermes RDP — Project Handoff

Last updated: 2026-08-07

## 1. Product vector

Hermes RDP is evolving from a reverse-RDP experiment into a small self-hosted **remote access control plane**:

> One public Linux server provides controlled remote access to multiple Windows PCs. Every PC gets its own persistent endpoint, credentials and state; pairing, monitoring and control are available through Telegram.

The product is **not** positioned as an SSH wrapper or an FRP replacement. OpenSSH is the current transport implementation. The actual product is the managed multi-device remote-access system around it.

## 2. Current architecture

```text
                           Telegram user
                                |
                                v
                     +---------------------+
                     | Telegram Dashboard  |
                     +----------+----------+
                                |
                                v
                     +---------------------+
                     | Hermes Controller   |
                     | HTTPS API           |
                     | SQLite Registry     |
                     | Command Queue       |
                     | Telemetry           |
                     +----------+----------+
                                |
                     +----------v----------+
                     | Dedicated OpenSSH   |
                     | sshd :7000          |
                     +-----+----------+-----+
                           |          |
                 reverse SSH          reverse SSH
                           |          |
                    +------v---+   +--v-------+
                    | Windows  |   | Windows  |
                    | Agent    |   | Agent    |
                    | ssh.exe  |   | ssh.exe  |
                    | RDP 3389 |   | RDP 3389 |
                    +----------+   +----------+
                         |              |
                      :53389         :53390 ...
                         |              |
                         +------ Remote RDP client
```

Server side:

- `hermes-rdp.service`: HTTPS API + Telegram bot + SQLite registry.
- `hermes-rdp-sshd.service`: isolated OpenSSH daemon for reverse forwarding.
- administrative SSH on port 22 is separate and must not be replaced by Hermes.
- RDP endpoint pool defaults to `53389–53420`.

Windows side:

- built-in `ssh.exe` and `ssh-keygen.exe` are used;
- `HermesRdpAgent.ps1` runs from Scheduled Task as `SYSTEM`;
- each PC has its own Ed25519 keypair, API token, device ID and RDP port;
- private SSH key stays on Windows;
- server stores the public key and authorizes only its assigned port through `permitlisten`;
- API HTTPS certificate is pinned; SSH host key is received through the pinned API and stored in dedicated `known_hosts`.

## 3. How the project got here

Major evolution:

```text
reverse RDP idea
  -> FRP server/client
  -> static public endpoint
  -> multi-PC registry
  -> Telegram dashboard
  -> pairing codes
  -> per-device API tokens
  -> LIVE telemetry
  -> ON/OFF/RESTART
  -> TLS certificate pinning
  -> Windows/server installers
  -> backup/update/uninstall
  -> Defender false-positive on FRP binary
  -> decision to remove FRP
  -> Windows system OpenSSH
  -> isolated server sshd
  -> per-device Ed25519 keys
  -> permitlisten isolation
  -> SSH host-key pinning
  -> atomic pairing/revoke/port reuse design
  -> successful real external RDP over mobile data
  -> multiple devices observed registering and using assigned ports
```

`v1.1.0` is the OpenSSH transition release and is already published on GitHub.

## 4. Confirmed real-world result

The important milestone is no longer theoretical: a Windows PC was paired successfully, the installer completed, the reverse OpenSSH path came up, and Microsoft Remote Desktop connected from a phone using mobile data rather than the Windows PC's LAN.

This confirmed the real path:

```text
mobile network
    -> public Linux server RDP endpoint
    -> reverse OpenSSH forwarding
    -> Windows 127.0.0.1:3389
```

The user later also confirmed that devices are being added and ports work. Formal acceptance of every multi-device/recovery/control scenario is still incomplete.

## 5. Main open product bug: state/control semantics

Current Telegram device view can show apparently contradictory data such as:

```text
PC ONLINE
SSH tunnel: stopped
Endpoint: available
RDP connections: active
```

This can appear both after ON and after OFF even though endpoints/RDP work.

The current UI conflates several independent states. They must be separated:

1. **Agent connectivity**: ONLINE / OFFLINE (heartbeat/API reachability).
2. **Desired access state**: ON / OFF (`devices.enabled`).
3. **Command state**: queued / executing / success / failed / timeout.
4. **Actual SSH transport state**: connected / disconnected.
5. **Server endpoint state**: open / closed.
6. **RDP session state**: active sessions / none.

Important: a PC should remain `ONLINE` while RDP access is `OFF`, because the agent must remain connected to the API so it can receive the next `ON` command.

### Current command flow

Telegram currently:

- immediately calls `set_enabled()`;
- queues `on`, `off` or `restart`;
- for `off`, also calls the server tunnel-close helper;
- replies only with “command sent”.

Windows agent polls every ~3 seconds. It sends telemetry, receives a pending command in the telemetry response, executes it and uploads `command-result`.

The database already stores enough information for a better UX:

- `enabled`;
- `pending_command`;
- `pending_created_at`;
- `command_seq`;
- `last_result_json`.

Telegram currently does not expose this lifecycle clearly.

## 6. Likely reason for false `SSH tunnel: stopped`

`HermesRdpAgent.ps1` identifies Hermes SSH processes with a strict `Win32_Process.CommandLine` match. The process must contain both:

- the configured private-key path;
- the exact reverse forwarding string `0.0.0.0:<rdp_port>:127.0.0.1:3389`.

The installer uses a looser check and only searches for an `ssh.exe` process containing the SSH key path.

Therefore the installer can consider the tunnel running while telemetry reports it stopped. This is a strong candidate but **must be verified on an actual test Windows machine before declaring it the final root cause**.

A second possibility is an orphan/legacy SSH process that holds the endpoint but is not recognized by the current agent matcher.

## 7. OFF behavior must be proven, not inferred

One stale telemetry frame immediately after pressing OFF is expected because the agent sends telemetry before receiving the pending command.

However after command completion the required behavior is:

```text
Agent: ONLINE
Desired RDP access: OFF
SSH: disconnected
Endpoint: CLOSED
RDP sessions through endpoint: none
```

If the endpoint stays open, investigate separately:

- whether Windows executed the command;
- whether `Stop-SshTunnel` found the correct ssh.exe process;
- whether the server `close_tunnel` helper killed the correct sshd child/listener;
- whether a second/orphan process reopened the endpoint.

Do not treat “command sent” as command success.

## 8. Telegram Dashboard v2 direction

The dashboard should become state-driven instead of button-driven.

Recommended device status block:

```text
AGENT            ONLINE
RDP ACCESS       ENABLED / DISABLED
SSH TUNNEL       CONNECTED / DISCONNECTED
ENDPOINT         OPEN / CLOSED
RDP SESSIONS     N active
LAST COMMAND     success / failed / pending + timestamp
```

Buttons should be contextual:

- access enabled: `DISABLE ACCESS`, `RESTART TUNNEL`;
- access disabled: `ENABLE ACCESS`;
- command pending: show progress and prevent duplicate contradictory commands;
- active RDP session + OFF/RESTART: show confirmation because it will disconnect the session.

Command progression should be visible:

```text
queued -> delivered -> executing -> success / failed / timeout
```

The current “external clients” field should not claim `127.0.0.1` is an external RDP client. Windows sees the SSH-forwarded source locally. If true external source IPs are needed, observe them server-side before forwarding.

## 9. Windows legacy ACL installer defect

A real upgrade attempt from the old Hermes/WinMon/FRP directory failed because a protected legacy key was not readable during recursive backup.

Current `main` still contains the fragile pattern:

- create backup **inside** `C:\ProgramData\HermesRDP\backups`;
- enumerate old directory;
- recursively `Copy-Item` protected children.

The intended fix is:

1. stop old tasks/processes;
2. move/rename the whole old Hermes directory to a sibling path such as `HermesRDP-legacy-<timestamp>`;
3. same-volume rename should avoid reading every protected child;
4. only on access failure apply scoped `takeown` + `icacls` to the old Hermes directory;
5. create a clean new directory;
6. only then perform pairing.

A branch named `fix/windows-legacy-acl-backup` was created in an earlier session, but the actual fix was not confirmed merged. Verify GitHub before using it.

## 10. Reliability gaps

Before calling the product stable, test/close:

- Windows reboot -> automatic tunnel recovery;
- temporary Windows network loss -> reconnect;
- Linux server reboot -> services + endpoints recover;
- controller restart without breaking tunnel behavior;
- at least two simultaneous devices with different ports and keys;
- first key cannot claim second device port;
- OFF / ON / RESTART exact state transitions;
- DELETE revokes API token and SSH key;
- DELETE closes endpoint;
- freed port can be safely reused;
- legacy reinstall path;
- server update and rollback;
- Windows agent update and rollback.

Current update scripts create backups, but do not yet provide a full transactional health-check + automatic rollback contract for all runtime failures.

## 11. Documentation audit

The user explicitly dislikes the current documentation and wants the quality/visual explanation restored.

This is justified by repository state:

- old `v1.0.7` `ARCHITECTURE.md` was much richer: goals, boundaries, server/client roles, Mermaid component diagram, pairing sequence, command sequence, data model, trust flow, failure behavior;
- current OpenSSH `ARCHITECTURE.md` became much shorter and lost much of that explanatory structure;
- `DEVELOPMENT.md` still contains stale FRPS/FRPC architectural rules;
- `ROADMAP.md` still includes obsolete FRP items;
- `WEBSITE.md` still contains stale `v1.0.7`/FRP maintenance wording;
- current README previously claimed `v1.1.0` release was not yet published, but `v1.1.0` is now published.

Required direction: restore the **structure and clarity** of the old documentation, but rewrite all technical content for the OpenSSH architecture.

## 12. README audit

The user wants the polished top section from the old README restored.

`v1.0.7` had visual badges/buttons for:

- latest release;
- CI;
- MIT license;
- Windows;
- Ubuntu/Debian.

It also clearly stated the important architectural principle:

> All Windows PCs are equal clients. There is no special “main PC”; only the Linux Hermes server is special.

This principle should return prominently to the current README.

README desired flow:

```text
logo/title + product statement
badges / website / docs / release links
what Hermes solves
large architecture diagram
key capabilities
quick start
Telegram dashboard behavior
security model
operations / update
full documentation index
release status
```

## 13. Website audit

The current site is technically competent (static HTML/CSS/JS, responsive, security headers, no trackers/runtime dependencies) but the user dislikes both design and copy.

Do not keep patching the current visual structure indefinitely. Plan a **Website v2** after control/state behavior is stable.

The first 5–10 seconds should explain the product before the implementation details:

```text
Home PC ----\
Office PC ----> Hermes Server ----> Remote Desktop from anywhere
Laptop ------/       |
                     +---- Telegram control
```

Then explain OpenSSH, Ed25519, pinning and isolation as security/architecture details.

The old/current site design itself is not a product requirement; the redesign should be evaluated on clarity, visual hierarchy, architecture illustration and credible product presentation.

## 14. Release direction

Do not add unrelated features before stability.

Recommended release path:

- use `v1.1.x` for critical correctness hotfixes if required immediately;
- target **`v1.2.0 — Stabilization`** as the coherent next product milestone.

Suggested PR groups:

1. state + tunnel correctness;
2. recovery + update + rollback;
3. Telegram Dashboard v2;
4. documentation + README rebuild;
5. Website v2;
6. full acceptance + release.

## 15. Working style for future chats

The user prefers:

- Russian language;
- direct technical communication;
- one stage at a time during live infrastructure work;
- copy-paste commands rather than manual `nano`/`vim` editing;
- explicit verification after each stage;
- do not claim PASS without output/result;
- separate rollback command where practical;
- do not weaken Microsoft Defender to make the project work;
- documentation should be visual and explanatory, with arrows/diagrams and architecture, not sparse placeholders.

Never request or echo secrets such as bot tokens, pairing codes, fingerprints, private keys or device tokens.