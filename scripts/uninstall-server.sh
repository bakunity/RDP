#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run through sudo." >&2
  exit 1
fi

read -r -p "Type REMOVE to uninstall Hermes RDP server: " ANSWER
[[ "$ANSWER" == "REMOVE" ]] || exit 1

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/var/backups/hermes-rdp/uninstall-$STAMP"
install -d -m 0700 "$BACKUP"

for path in \
  /etc/hermes-rdp \
  /opt/hermes-rdp \
  /var/lib/hermes-rdp \
  /etc/systemd/system/hermes-rdp.service \
  /etc/systemd/system/hermes-rdp-sshd.service \
  /etc/sudoers.d/hermes-rdp; do
  [[ -e "$path" ]] && cp -a --parents "$path" "$BACKUP/"
done

systemctl disable --now \
  hermes-rdp.service \
  hermes-rdp-sshd.service 2>/dev/null || true

rm -f \
  /etc/systemd/system/hermes-rdp.service \
  /etc/systemd/system/hermes-rdp-sshd.service \
  /etc/sudoers.d/hermes-rdp \
  /usr/local/bin/hermes-rdpctl \
  /usr/local/bin/hermes-rdp-authorized-keys \
  /usr/local/sbin/hermes-rdp-close-tunnel

systemctl daemon-reload

echo "Hermes RDP services removed."
echo "Data and configuration were preserved."
echo "Backup: $BACKUP"
