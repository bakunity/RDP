#!/usr/bin/env bash
set -Eeuo pipefail

CONFIG=/etc/hermes-rdp/config.json
CERTBOT=/usr/local/bin/certbot
LOCK=/run/hermes-rdp-cert-renew.lock

if [[ ! -x "$CERTBOT" ]]; then
  echo "Hermes certificate renewal: certbot is unavailable at $CERTBOT" >&2
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

exec /usr/bin/flock -w 300 "$LOCK" \
  "$CERTBOT" renew \
    --cert-name "$CERT_NAME" \
    --quiet \
    --non-interactive
