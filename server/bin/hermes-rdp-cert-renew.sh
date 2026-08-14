#!/usr/bin/env bash
set -Eeuo pipefail

CONFIG=/etc/hermes-rdp/config.json
CERTBOT=/usr/local/bin/certbot
STATE_REFRESH=/usr/local/sbin/hermes-rdp-cert-state-refresh
LOCK=/run/hermes-rdp-cert-renew.lock

if [[ ! -x "$CERTBOT" ]]; then
  echo "Hermes certificate renewal: certbot is unavailable at $CERTBOT" >&2
  exit 1
fi
if [[ ! -x "$STATE_REFRESH" ]]; then
  echo "Hermes certificate renewal: state refresher is unavailable at $STATE_REFRESH" >&2
  exit 1
fi
if [[ ! -s "$CONFIG" ]]; then
  echo "Hermes certificate renewal: missing $CONFIG" >&2
  exit 1
fi
if ! command -v flock >/dev/null 2>&1; then
  echo "Hermes certificate renewal: flock is unavailable" >&2
  exit 1
fi

CERT_NAME="$(python3 - <<'PY'
import json
from pathlib import Path

path = Path('/etc/hermes-rdp/config.json')
data = json.loads(path.read_text(encoding='utf-8'))
trusted = data.get('trusted_rdp_certificate') or {}
if trusted.get('enabled') is not True:
    raise SystemExit('trusted RDP certificate is not enabled')
name = str(trusted.get('cert_name') or '').strip()
if not name:
    raise SystemExit('trusted RDP certificate name is missing')
print(name)
PY
)"

exec 9>"$LOCK"
if ! /usr/bin/flock -w 300 9; then
  echo "Hermes certificate renewal: timed out waiting for lock" >&2
  exit 1
fi

"$CERTBOT" renew \
  --cert-name "$CERT_NAME" \
  --quiet \
  --non-interactive

"$STATE_REFRESH" >/dev/null
