# Hermes RDP — Milestone History

This is a compact project history, not a transcript.

## 2026-08-05 — First public product shape

Hermes RDP evolved from a single reverse-RDP setup into a multi-PC system with:

- Linux controller;
- FRP gateway;
- per-device ports;
- Telegram dashboard;
- pairing;
- telemetry;
- ON/OFF/RESTART;
- install/update scripts;
- first public releases `v1.0.x`.

## 2026-08-06 — FRP deployment problem discovered

The official FRP Windows archive triggered Microsoft Defender detection/quarantine in real installation testing.

The upstream archive hash matched the expected pinned hash, but the operational experience was unacceptable. The project decision was to remove FRP from the core Windows transport instead of requiring Defender exclusions.

## 2026-08-06 — OpenSSH redesign

The transport architecture was rewritten around system OpenSSH:

- Windows built-in `ssh.exe` and `ssh-keygen.exe`;
- isolated server sshd on the tunnel port;
- per-device Ed25519 keypair;
- public key stored server-side;
- private key retained on Windows;
- `AuthorizedKeysCommand` + `permitlisten` per endpoint;
- pinned SSH host key delivered through pinned HTTPS API;
- FRP service/binary removed from the active architecture.

## 2026-08-06 — Clean server validation

A test server was fully reset without touching system administrative SSH, then installed with the OpenSSH version.

Confirmed:

- Hermes controller active/enabled;
- Hermes dedicated sshd active/enabled;
- API listening;
- tunnel sshd listening;
- RDP pool closed before device pairing;
- FRP absent.

## 2026-08-06 — Windows legacy ACL failure found

First Windows upgrade test over an old Hermes/WinMon/FRP directory failed because recursive backup tried to read a protected legacy private-key file.

Manual scoped cleanup/archival allowed the test to continue. The required permanent installer design became whole-directory legacy archival with ACL fallback only when needed.

## 2026-08-06 — First successful OpenSSH Windows install

A clean Windows OpenSSH client installation completed successfully:

- device paired;
- persistent RDP port allocated;
- Scheduled Task created;
- reverse SSH started;
- installer printed successful completion.

## 2026-08-06 — Real external RDP PASS

Microsoft Remote Desktop connected from a phone using mobile data. This confirmed full end-to-end external access through the Linux server and reverse OpenSSH tunnel.

This is the key proof that the transport architecture works in the intended real-world topology.

## 2026-08-06 — Documentation/site refresh PR

A large docs/site refresh was merged and Vercel production updated.

It correctly replaced public FRP marketing content with OpenSSH terminology, but later review found that documentation quality/architecture explanation regressed compared with `v1.0.7`, and several documentation files remained internally stale.

The user does not consider this site/docs version final.

## 2026-08-06 — `v1.1.0` published

GitHub Release `v1.1.0` was successfully published. It is the first published OpenSSH transport release.

## 2026-08-07 — Multi-device use and control-state audit

The user reported that devices are adding successfully and assigned ports work.

During ON/OFF testing the Telegram dashboard showed contradictory state such as:

- device ONLINE;
- SSH tunnel reported stopped;
- endpoint/RDP actually usable.

This triggered a full product audit.

Main conclusion: core transport works, but the control plane/state model must be stabilized before calling the project finished.

The next target became a stabilization cycle focused on:

1. truthful state and deterministic command lifecycle;
2. remaining reboot/network recovery;
3. safe update/rollback;
4. Dashboard v2;
5. full documentation/README rebuild;
6. Website v2;
7. final acceptance.

## 2026-08-07 — Persistent cross-chat context created

Created repository folder `context/` so future conversations can reconstruct the project without relying on the previous long chat.

The context intentionally excludes secrets and stores architecture, current state, durable decisions, audit conclusions and next-work protocol.

## 2026-08-07 — Windows reboot + Telegram OFF/ON PASS

Further live acceptance closed several previously open questions:

- the tested Windows PC was rebooted and Hermes recovered automatically enough for RDP to work again;
- pressing OFF in Telegram disconnected the active RDP session / made access unusable;
- pressing ON restored RDP access;
- the user explicitly confirmed the functionality works.

The remaining `SSH tunnel: stopped` inconsistency is therefore treated as a telemetry/state-representation bug rather than proof of a broken transport.

The acceptance matrix now distinguishes user-visible access behavior from a separate low-level endpoint-listener measurement.

## 2026-08-07 — Latest-session handoff protocol added

Added `context/LAST_SESSION.md` as the compact per-chat delta. `context/README.md` and `SESSION_PROTOCOL.md` now require future long chats to refresh this file before migration, and to propagate real PASS/FAIL changes into the durable context files.
