#!/usr/bin/env bash
set -Eeuo pipefail

REPO="bakunity/RDP"
REF="${HERMES_RDP_REF:-main}"

if [[ ${EUID} -ne 0 ]]; then
  echo "Run through sudo." >&2
  exit 1
fi
if [[ ! -s /etc/hermes-rdp/config.json ]]; then
  echo "Hermes RDP is not installed." >&2
  exit 1
fi
if ! python3 - <<'PY'
import json
with open("/etc/hermes-rdp/config.json", encoding="utf-8") as handle:
    data = json.load(handle)
raise SystemExit(0 if "ssh_bind_port" in data else 1)
PY
then
  echo "This server still uses FRP." >&2
  echo "Run install-server.sh with --migrate for the v1.1 OpenSSH migration." >&2
  exit 2
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/hermes-rdp/update-$STAMP"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

install -d -m 0700 "$BACKUP"
for path in \
  /opt/hermes-rdp \
  /etc/hermes-rdp/config.json \
  /etc/hermes-rdp/sshd_config \
  /etc/systemd/system/hermes-rdp.service \
  /etc/systemd/system/hermes-rdp-sshd.service; do
  [[ -e "$path" ]] && cp -a --parents "$path" "$BACKUP/"
done

curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" -o "$WORK/source.tar.gz"
tar -xzf "$WORK/source.tar.gz" -C "$WORK"
ROOT="$(find "$WORK" -maxdepth 1 -mindepth 1 -type d -name 'RDP-*' | head -n1)"
test -f "$ROOT/server/pyproject.toml"

rm -rf /opt/hermes-rdp/app/hermes_rdp
cp -a "$ROOT/server/hermes_rdp" /opt/hermes-rdp/app/hermes_rdp
chown -R root:root /opt/hermes-rdp/app

install -m 0644 \
  "$ROOT/server/systemd/hermes-rdp.service" \
  /etc/systemd/system/hermes-rdp.service
install -m 0644 \
  "$ROOT/server/systemd/hermes-rdp-sshd.service" \
  /etc/systemd/system/hermes-rdp-sshd.service

python3 - "$REF" <<'PY'
import json
import sys
from pathlib import Path

ref = sys.argv[1]
path = Path("/etc/hermes-rdp/config.json")
data = json.loads(path.read_text(encoding="utf-8"))
data["client_installer_url"] = (
    "https://raw.githubusercontent.com/bakunity/RDP/"
    f"{ref}/scripts/install-client.ps1"
)
data["repository_ref"] = ref
path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY
chmod 0640 /etc/hermes-rdp/config.json
chown root:hermes-rdp /etc/hermes-rdp/config.json

PYTHONPATH=/opt/hermes-rdp/app \
  python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp
/usr/sbin/sshd -t -f /etc/hermes-rdp/sshd_config

systemctl daemon-reload
systemctl restart hermes-rdp-sshd.service hermes-rdp.service
sleep 2
systemctl is-active hermes-rdp-sshd.service hermes-rdp.service

echo "Updated. Backup: $BACKUP"
