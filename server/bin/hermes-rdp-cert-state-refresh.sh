#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

CONFIG=/etc/hermes-rdp/config.json
STATE=/etc/hermes-rdp/trusted-rdp-cert-state.json
TMP="${STATE}.tmp.$$"

cleanup() {
  rm -f "$TMP"
}
trap cleanup EXIT

if [[ ! -s "$CONFIG" ]]; then
  echo "Hermes certificate state: missing $CONFIG" >&2
  exit 1
fi

readarray -t CERT_INFO < <(
  python3 - <<'PY'
import json
from pathlib import Path

path = Path('/etc/hermes-rdp/config.json')
data = json.loads(path.read_text(encoding='utf-8'))
trusted = data.get('trusted_rdp_certificate') or {}
if trusted.get('enabled') is not True:
    raise SystemExit('trusted RDP certificate is not enabled')
name = str(trusted.get('cert_name') or '').strip()
live = str(trusted.get('live_dir') or '').strip()
if not name or not live:
    raise SystemExit('trusted RDP certificate configuration is incomplete')
print(name)
print(live)
PY
)

CERT_NAME="${CERT_INFO[0]:-}"
LIVE_DIR="${CERT_INFO[1]:-}"
CERT="$LIVE_DIR/cert.pem"

if [[ ! -s "$CERT" ]]; then
  echo "Hermes certificate state: missing $CERT" >&2
  exit 1
fi

openssl x509 -in "$CERT" -noout -checkip "$CERT_NAME" >/dev/null 2>&1 || {
  echo "Hermes certificate state: certificate identity mismatch" >&2
  exit 1
}

THUMBPRINT="$(
  openssl x509 -in "$CERT" -noout -fingerprint -sha1 |
    cut -d= -f2 |
    tr -d ':' |
    tr '[:lower:]' '[:upper:]'
)"
SHA256="$(
  openssl x509 -in "$CERT" -noout -fingerprint -sha256 |
    cut -d= -f2 |
    tr -d ':' |
    tr '[:lower:]' '[:upper:]'
)"
SERIAL="$(openssl x509 -in "$CERT" -noout -serial | cut -d= -f2 | tr '[:lower:]' '[:upper:]')"
NOT_AFTER="$(openssl x509 -in "$CERT" -noout -enddate | cut -d= -f2-)"

python3 - "$TMP" "$CERT_NAME" "$THUMBPRINT" "$SHA256" "$SERIAL" "$NOT_AFTER" <<'PY'
import json
import sys
import time
from pathlib import Path

path = Path(sys.argv[1])
payload = {
    'enabled': True,
    'cert_name': sys.argv[2],
    'thumbprint': sys.argv[3],
    'sha256': sys.argv[4],
    'serial': sys.argv[5],
    'not_after': sys.argv[6],
    'generated_at': int(time.time()),
}
path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
PY

chown root:hermes-rdp "$TMP"
chmod 0640 "$TMP"
mv -f "$TMP" "$STATE"
trap - EXIT

echo "CERT_STATE=REFRESHED"
