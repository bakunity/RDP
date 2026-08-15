#!/usr/bin/env bash
set -Eeuo pipefail

REPO="bakunity/RDP"
REF="${HERMES_RDP_REF:-}"

if [[ ${EUID} -ne 0 ]]; then
  echo "Run through sudo." >&2
  exit 1
fi
if ! [[ "$REF" =~ ^[0-9a-f]{40}$ ]]; then
  echo "HERMES_RDP_REF must be the exact 40-character commit SHA under acceptance." >&2
  exit 2
fi
if [[ ! -s /etc/hermes-rdp/config.json ]]; then
  echo "Existing Hermes server config was not found; refusing clean-reinstall fixture helper." >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/hermes-rdp/clean-reinstall-$STAMP"
WORK="$(mktemp -d)"
APT_LOG="$WORK/apt-update.log"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT
install -d -m 0700 "$BACKUP"

# The reported fixture has overlapping one-line APT entries rather than byte-identical
# duplicates. Merge only simple deb/deb-src entries that have the same type + URI +
# suite, preserve the union/order of components, then validate and roll back on any
# remaining duplicate warning or apt-get failure. Complex option/comment lines are left
# untouched by this bounded fixture helper.
cp -a /etc/apt/sources.list "$BACKUP/sources.list"
python3 - <<'PY'
from pathlib import Path

path = Path('/etc/apt/sources.list')
lines = path.read_text(encoding='utf-8').splitlines()
out: list[str | None] = []
first: dict[tuple[str, str, str], int] = {}
components: dict[tuple[str, str, str], list[str]] = {}

for raw in lines:
    stripped = raw.strip()
    parts = stripped.split()
    simple = (
        len(parts) >= 4
        and parts[0] in {'deb', 'deb-src'}
        and '[' not in stripped
        and '#' not in stripped
    )
    if not simple:
        out.append(raw)
        continue

    key = (parts[0], parts[1], parts[2])
    if key not in first:
        first[key] = len(out)
        components[key] = []
        out.append(None)
    for component in parts[3:]:
        if component not in components[key]:
            components[key].append(component)

for key, index in first.items():
    out[index] = ' '.join((*key, *components[key]))

path.write_text('\n'.join(line or '' for line in out) + '\n', encoding='utf-8')
PY

if ! apt-get update -qq >"$APT_LOG" 2>&1 || grep -q 'is configured multiple times' "$APT_LOG"; then
  cp -a "$BACKUP/sources.list" /etc/apt/sources.list
  apt-get update -qq >/dev/null 2>&1 || true
  cat "$APT_LOG" >&2 || true
  echo "APT semantic cleanup failed; rollback PASS; Hermes was not removed." >&2
  exit 1
fi
echo "APT cleanup: PASS"

curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" -o "$WORK/source.tar.gz"
tar -xzf "$WORK/source.tar.gz" -C "$WORK"
SOURCE_ROOT="$(find "$WORK" -maxdepth 1 -mindepth 1 -type d -name 'RDP-*' | head -n1)"
if [[ -z "$SOURCE_ROOT" || ! -f "$SOURCE_ROOT/scripts/uninstall-server.sh" || ! -f "$SOURCE_ROOT/scripts/install.sh" ]]; then
  echo "Exact Hermes source ref could not be validated; nothing was uninstalled." >&2
  exit 1
fi

# Normal uninstall first: it stops services/timers, removes Hermes-managed nginx ACME
# routing and creates its own rollback backup. Then purge all Hermes identity/state so
# the next install creates a fresh DB, API TLS key, SSH host key and system accounts.
printf 'REMOVE\n' | bash "$SOURCE_ROOT/scripts/uninstall-server.sh"
rm -rf \
  /etc/hermes-rdp \
  /opt/hermes-rdp \
  /var/lib/hermes-rdp \
  /var/lib/hermes-rdp-tunnel \
  /var/www/hermes-rdp-acme

if id hermes-tunnel >/dev/null 2>&1; then
  userdel hermes-tunnel
fi
if id hermes-rdp >/dev/null 2>&1; then
  userdel hermes-rdp
fi
getent group hermes-tunnel >/dev/null 2>&1 && groupdel hermes-tunnel || true
getent group hermes-rdp >/dev/null 2>&1 && groupdel hermes-rdp || true
systemctl daemon-reload

if [[ -e /etc/hermes-rdp || -e /opt/hermes-rdp || -e /var/lib/hermes-rdp ]] || \
   id hermes-rdp >/dev/null 2>&1 || id hermes-tunnel >/dev/null 2>&1; then
  echo "Hermes clean-state verification failed; reinstall was not started." >&2
  exit 1
fi
echo "Hermes clean state: PASS"
echo "ACME certificate lineage/backups and shared host packages/firewall policy were intentionally preserved."

bash "$SOURCE_ROOT/scripts/install.sh"
