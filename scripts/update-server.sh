#!/usr/bin/env bash
set -Eeuo pipefail

REPO="bakunity/RDP"
REF="${HERMES_RDP_REF:-main}"
if [[ ${EUID} -ne 0 ]]; then
  echo "Run through sudo." >&2
  exit 1
fi
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/hermes-rdp/update-$STAMP"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
install -d -m 0700 "$BACKUP"
cp -a /opt/hermes-rdp /etc/hermes-rdp/config.json /etc/systemd/system/hermes-rdp.service "$BACKUP/"
curl -fsSL "https://github.com/$REPO/archive/refs/heads/$REF.tar.gz" -o "$WORK/source.tar.gz"
tar -xzf "$WORK/source.tar.gz" -C "$WORK"
ROOT="$(find "$WORK" -maxdepth 1 -mindepth 1 -type d -name 'RDP-*' | head -n1)"
test -f "$ROOT/server/pyproject.toml"
rm -rf /opt/hermes-rdp/app/hermes_rdp
cp -a "$ROOT/server/hermes_rdp" /opt/hermes-rdp/app/hermes_rdp
chown -R root:root /opt/hermes-rdp/app
install -m 0644 "$ROOT/server/systemd/hermes-rdp.service" /etc/systemd/system/hermes-rdp.service
systemctl daemon-reload
systemctl restart hermes-rdp.service
sleep 2
systemctl is-active hermes-rdp.service
echo "Updated. Backup: $BACKUP"
