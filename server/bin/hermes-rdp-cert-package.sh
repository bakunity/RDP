#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

CONFIG=/etc/hermes-rdp/config.json

if [[ ${EUID} -ne 0 ]]; then
  echo "Hermes certificate package helper must run as root" >&2
  exit 1
fi
if [[ ! -s "$CONFIG" ]]; then
  echo "Hermes certificate package helper: missing $CONFIG" >&2
  exit 1
fi
for command in openssl python3 base64; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Hermes certificate package helper: missing $command" >&2
    exit 1
  }
done

readarray -t CERT_INFO < <(python3 - <<'PY'
import json
from pathlib import Path

path = Path('/etc/hermes-rdp/config.json')
data = json.loads(path.read_text(encoding='utf-8'))
trusted = data.get('trusted_rdp_certificate') or {}
if trusted.get('enabled') is not True:
    raise SystemExit('trusted RDP certificate is not enabled')
cert_name = str(trusted.get('cert_name') or '').strip()
live_dir = str(trusted.get('live_dir') or '').strip()
if not cert_name or not live_dir:
    raise SystemExit('trusted RDP certificate configuration is incomplete')
print(cert_name)
print(live_dir)
PY
)

if ((${#CERT_INFO[@]} != 2)); then
  echo "Hermes certificate package helper: invalid trusted certificate config" >&2
  exit 1
fi
CERT_NAME="${CERT_INFO[0]}"
LIVE="${CERT_INFO[1]}"
CERT="$LIVE/cert.pem"
CHAIN="$LIVE/chain.pem"
KEY="$LIVE/privkey.pem"

for path in "$CERT" "$CHAIN" "$KEY"; do
  [[ -s "$path" ]] || {
    echo "Hermes certificate package helper: missing certificate material" >&2
    exit 1
  }
done

openssl x509 -in "$CERT" -noout -checkip "$CERT_NAME" >/dev/null 2>&1 || {
  echo "Hermes certificate package helper: certificate identity mismatch" >&2
  exit 1
}

WORK="$(mktemp -d)"
cleanup() {
  rm -rf "$WORK"
}
trap cleanup EXIT

PASSWORD="$(openssl rand -hex 24)"
export HERMES_PFX_PASSWORD="$PASSWORD"
PFX="$WORK/hermes-rdp.pfx"

openssl pkcs12 -export \
  -out "$PFX" \
  -inkey "$KEY" \
  -in "$CERT" \
  -certfile "$CHAIN" \
  -name "Hermes RDP $CERT_NAME" \
  -passout env:HERMES_PFX_PASSWORD \
  >/dev/null 2>&1

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
NOT_AFTER="$(openssl x509 -in "$CERT" -noout -enddate | cut -d= -f2-)"
PFX_BASE64="$(base64 -w 0 "$PFX")"

python3 - "$CERT_NAME" "$THUMBPRINT" "$SHA256" "$NOT_AFTER" "$PASSWORD" "$PFX_BASE64" <<'PY'
import json
import sys

cert_name, thumbprint, sha256, not_after, password, pfx_base64 = sys.argv[1:]
print(json.dumps({
    'cert_name': cert_name,
    'thumbprint': thumbprint,
    'sha256': sha256,
    'not_after': not_after,
    'password': password,
    'pfx_base64': pfx_base64,
}, separators=(',', ':')))
PY
