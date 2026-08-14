# Hermes RDP — Last Session Handoff

Updated: 2026-08-14
Status: **CHAT BOUNDARY DELTA / NON-AUTHORITATIVE**

Primary truth remains `ACTIVE_WORK.md` / `CURRENT_STATE.md` / `NEXT_WORK.md`.

## Where this chat stopped

The stabilization/release work is complete enough to move on:

- stable release is **v1.2.1**;
- rich product README with badges and full Hermes RDP description is restored;
- `v1.2.0` remains historical packaging-error release and is not rewritten;
- prepared release-workflow hardening branch `fix/release-tag-head-v2` exists at `ef32b8dd95ffa1c274dc1749eae736867d2fb74b`, but no PR was successfully opened yet.

The active workstream changed to **trusted Microsoft RDP certificate using the public IP**. Domain use is intentionally deferred unless a concrete need appears.

## Certificate evidence already accepted

### CERT-001 — PASS

Live server inventory:

- Debian GNU/Linux 13 (trixie);
- Certbot initially absent;
- Nginx absent;
- no listeners on TCP `80` or `443` at check time.

### CERT-002 — PASS

Certbot installation completed successfully.

Observed final output:

```text
=== CERT-002 ===
certbot 5.7.0
```

Do **not** ask the user to reinstall Certbot or repeat CERT-001 without a concrete regression reason.

No certificate has been issued yet. No Windows RDP listener/certificate state has been changed yet.

## Exact resume action

Start with **CERT-003 only**:

1. verify TCP `80` is reachable from the public Internet for ACME HTTP validation;
2. if reachable, do a bounded staging/test public-IP certificate issuance with Certbot standalone;
3. inspect identity/SAN/chain before production use;
4. only later bind a trusted certificate to the Windows RDP listener, first on `SEC005 TEST`, preserving rollback.

Critical conceptual boundary: installing TLS only on the Linux/API side does not remove the Microsoft Remote Desktop certificate warning. The Windows RDP listener is the certificate presenter for the tunneled RDP connection.

Never put private keys, pairing codes, API tokens or ready-to-use secret material into context/chat.
