#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ${EUID} -ne 0 ]]; then
  echo "Run through sudo." >&2
  exit 1
fi
read -r -p "Remove Hermes RDP server services? Type REMOVE: " answer
[[ "$answer" == "REMOVE" ]] || exit 1
systemctl disable --now hermes-rdp.service frps.service 2>/dev/null || true
rm -f /etc/systemd/system/hermes-rdp.service /etc/systemd/system/frps.service
systemctl daemon-reload
rm -rf /opt/hermes-rdp /etc/frp
# Secrets and database are deliberately retained for recovery.
echo "Programs removed. Retained: /etc/hermes-rdp and /var/lib/hermes-rdp"
