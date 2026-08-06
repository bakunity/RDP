#!/usr/bin/env bash
set -Eeuo pipefail

REPO="bakunity/RDP"
REF="${HERMES_RDP_REF:-main}"
FRP_VERSION="0.70.1"
FRP_LINUX_SHA256="333da23d1b9009d7c01638e9ba38cf4600f7d37d393f854e96ee1396adefa9a6"
HOST=""
TELEGRAM_TOKEN=""
TELEGRAM_CHAT_ID=""
API_PORT=7443
FRP_PORT=7000
PORT_START=53389
PORT_END=53420
MIGRATE=0

usage() {
  cat <<'EOF'
Usage:
  install-server.sh --host HOST --telegram-token TOKEN --telegram-chat-id ID [options]

Options:
  --api-port PORT       HTTPS API port (default: 7443)
  --frp-port PORT       FRP control port (default: 7000)
  --port-start PORT     first RDP port (default: 53389)
  --port-end PORT       last RDP port (default: 53420)
  --migrate             back up and replace the existing Hermes FRP/bot setup
EOF
}

while (($#)); do
  case "$1" in
    --host) HOST="${2:?}"; shift 2 ;;
    --telegram-token) TELEGRAM_TOKEN="${2:?}"; shift 2 ;;
    --telegram-chat-id) TELEGRAM_CHAT_ID="${2:?}"; shift 2 ;;
    --api-port) API_PORT="${2:?}"; shift 2 ;;
    --frp-port) FRP_PORT="${2:?}"; shift 2 ;;
    --port-start) PORT_START="${2:?}"; shift 2 ;;
    --port-end) PORT_END="${2:?}"; shift 2 ;;
    --migrate) MIGRATE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ${EUID} -ne 0 ]]; then
  echo "Run as root or through sudo." >&2
  exit 1
fi
if [[ -z "$HOST" || -z "$TELEGRAM_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
  usage >&2
  exit 2
fi
if ! [[ "$API_PORT" =~ ^[0-9]+$ && "$FRP_PORT" =~ ^[0-9]+$ && "$PORT_START" =~ ^[0-9]+$ && "$PORT_END" =~ ^[0-9]+$ ]]; then
  echo "Ports must be integers." >&2
  exit 2
fi
if ((PORT_START > PORT_END)); then
  echo "port-start must not exceed port-end." >&2
  exit 2
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="/var/backups/hermes-rdp/$STAMP"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq ca-certificates curl tar unzip openssl python3 ufw >/dev/null

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"
SOURCE_ROOT=""
if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/../server/pyproject.toml" ]]; then
  SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  ARCHIVE="$WORK_DIR/source.tar.gz"
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" -o "$ARCHIVE"
  tar -xzf "$ARCHIVE" -C "$WORK_DIR"
  SOURCE_ROOT="$(find "$WORK_DIR" -maxdepth 1 -mindepth 1 -type d -name 'RDP-*' | head -n1)"
fi
if [[ -z "$SOURCE_ROOT" || ! -f "$SOURCE_ROOT/server/pyproject.toml" ]]; then
  echo "Unable to locate project source." >&2
  exit 1
fi

install -d -m 0700 "$BACKUP_DIR"
for path in \
  /etc/frp \
  /etc/hermes-rdp \
  /opt/hermes-rdp \
  /var/lib/hermes-rdp \
  /etc/systemd/system/frps.service \
  /etc/systemd/system/hermes-rdp.service \
  /etc/systemd/system/hermes-rdp-bot.service; do
  if [[ -e "$path" ]]; then
    cp -a --parents "$path" "$BACKUP_DIR/"
  fi
done
ln -sfn "$BACKUP_DIR" /var/backups/hermes-rdp/latest

if [[ -e /etc/systemd/system/hermes-rdp-bot.service || -d /opt/hermes-rdp-bot ]]; then
  if ((MIGRATE == 0)); then
    echo "Existing Hermes RDP bot detected. Re-run with --migrate after reviewing the backup path:" >&2
    echo "  $BACKUP_DIR" >&2
    exit 1
  fi
  systemctl disable --now hermes-rdp-bot.service 2>/dev/null || true
fi

getent group frp >/dev/null || groupadd --system frp
id frp >/dev/null 2>&1 || useradd --system --gid frp --home-dir /nonexistent --shell /usr/sbin/nologin frp
getent group hermes-rdp >/dev/null || groupadd --system hermes-rdp
id hermes-rdp >/dev/null 2>&1 || useradd --system --gid hermes-rdp --home-dir /var/lib/hermes-rdp --shell /usr/sbin/nologin hermes-rdp

install -d -m 0755 -o root -g root /opt/hermes-rdp/app
rm -rf /opt/hermes-rdp/app/hermes_rdp
cp -a "$SOURCE_ROOT/server/hermes_rdp" /opt/hermes-rdp/app/hermes_rdp
chown -R root:root /opt/hermes-rdp/app
cat > /usr/local/bin/hermes-rdpctl <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH=/opt/hermes-rdp/app
exec /usr/bin/python3 -m hermes_rdp.cli "$@"
EOF
chmod 0755 /usr/local/bin/hermes-rdpctl

FRP_ARCHIVE="$WORK_DIR/frp.tar.gz"
curl -fsSL "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_amd64.tar.gz" -o "$FRP_ARCHIVE"
echo "$FRP_LINUX_SHA256  $FRP_ARCHIVE" | sha256sum -c -
tar -xzf "$FRP_ARCHIVE" -C "$WORK_DIR"
install -m 0755 "$WORK_DIR/frp_${FRP_VERSION}_linux_amd64/frps" /usr/local/bin/frps

install -d -m 0750 -o root -g hermes-rdp /etc/hermes-rdp
install -d -m 0750 -o root -g frp /etc/frp
install -d -m 0750 -o root -g hermes-rdp /etc/hermes-rdp/tls
install -d -m 0750 -o root -g frp /etc/frp/tls
install -d -m 0750 -o hermes-rdp -g hermes-rdp /var/lib/hermes-rdp

if [[ ! -s /etc/hermes-rdp/frp-token ]]; then
  if [[ -s /etc/frp/token ]]; then
    tr -d '\r\n' < /etc/frp/token > /etc/hermes-rdp/frp-token
  else
    old_token=""
    if [[ -s /etc/frp/frps.toml ]]; then
      old_token="$(sed -n 's/^[[:space:]]*auth\.token[[:space:]]*=[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' /etc/frp/frps.toml 2>/dev/null | head -n1)"
    fi
    if [[ -n "$old_token" ]]; then
      printf '%s' "$old_token" > /etc/hermes-rdp/frp-token
    else
      openssl rand -base64 48 | tr -d '\n' > /etc/hermes-rdp/frp-token
    fi
  fi
fi
printf '%s\n' "$TELEGRAM_TOKEN" > /etc/hermes-rdp/telegram-token
chmod 0640 /etc/hermes-rdp/frp-token /etc/hermes-rdp/telegram-token
chown root:hermes-rdp /etc/hermes-rdp/frp-token /etc/hermes-rdp/telegram-token

API_TLS_DIR=/etc/hermes-rdp/tls
FRP_TLS_DIR=/etc/frp/tls

# Normalize common legacy FRP certificate names without replacing a complete setup.
if ((MIGRATE == 1)); then
  if [[ ! -s "$FRP_TLS_DIR/ca.crt" && -s "$FRP_TLS_DIR/ca.pem" ]]; then
    cp -a "$FRP_TLS_DIR/ca.pem" "$FRP_TLS_DIR/ca.crt"
  fi
  if [[ ! -s "$FRP_TLS_DIR/server.crt" && -s "$FRP_TLS_DIR/frps.crt" ]]; then
    cp -a "$FRP_TLS_DIR/frps.crt" "$FRP_TLS_DIR/server.crt"
  fi
  if [[ ! -s "$FRP_TLS_DIR/server.key" && -s "$FRP_TLS_DIR/frps.key" ]]; then
    cp -a "$FRP_TLS_DIR/frps.key" "$FRP_TLS_DIR/server.key"
  fi
fi

if [[ ! -s "$API_TLS_DIR/api.key" || ! -s "$API_TLS_DIR/api.crt" ]]; then
  SAN="DNS:$HOST"
  if [[ "$HOST" =~ ^[0-9a-fA-F:.]+$ ]]; then
    SAN="IP:$HOST"
  fi
  openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 825 \
    -subj "/CN=$HOST" -addext "subjectAltName=$SAN" \
    -keyout "$API_TLS_DIR/api.key" -out "$API_TLS_DIR/api.crt" >/dev/null 2>&1
fi
openssl x509 -in "$API_TLS_DIR/api.crt" -outform DER | sha256sum | awk '{print toupper($1)}' > "$API_TLS_DIR/api.sha256"

if [[ ! -s "$FRP_TLS_DIR/ca.crt" ]]; then
  openssl genrsa -out "$FRP_TLS_DIR/ca.key" 3072 >/dev/null 2>&1
  openssl req -x509 -new -sha256 -days 3650 -key "$FRP_TLS_DIR/ca.key" \
    -subj "/CN=Hermes RDP FRP CA" -out "$FRP_TLS_DIR/ca.crt" >/dev/null 2>&1
fi
if [[ ! -s "$FRP_TLS_DIR/server.key" || ! -s "$FRP_TLS_DIR/server.crt" ]]; then
  if [[ ! -s "$FRP_TLS_DIR/ca.key" ]]; then
    echo "Existing FRP CA certificate has no signing key and no complete server certificate pair." >&2
    echo "Restore server.crt/server.key or remove ca.crt to generate a new FRP CA." >&2
    exit 1
  fi
  SAN="DNS:$HOST"
  if [[ "$HOST" =~ ^[0-9a-fA-F:.]+$ ]]; then
    SAN="IP:$HOST"
  fi
  openssl genrsa -out "$FRP_TLS_DIR/server.key" 3072 >/dev/null 2>&1
  openssl req -new -sha256 -key "$FRP_TLS_DIR/server.key" -subj "/CN=$HOST" \
    -out "$WORK_DIR/frp-server.csr" >/dev/null 2>&1
  printf 'subjectAltName=%s\nextendedKeyUsage=serverAuth\n' "$SAN" > "$WORK_DIR/frp-server.ext"
  openssl x509 -req -sha256 -days 825 -in "$WORK_DIR/frp-server.csr" \
    -CA "$FRP_TLS_DIR/ca.crt" -CAkey "$FRP_TLS_DIR/ca.key" -CAcreateserial \
    -extfile "$WORK_DIR/frp-server.ext" -out "$FRP_TLS_DIR/server.crt" >/dev/null 2>&1
fi

install -m 0644 -o root -g hermes-rdp "$FRP_TLS_DIR/ca.crt" /etc/hermes-rdp/frp-ca.crt
chmod 0640 "$API_TLS_DIR/api.key"
chmod 0644 "$API_TLS_DIR/api.crt" "$API_TLS_DIR/api.sha256"
chown root:hermes-rdp "$API_TLS_DIR/api.key" "$API_TLS_DIR/api.crt" "$API_TLS_DIR/api.sha256"
if [[ -s "$FRP_TLS_DIR/ca.key" ]]; then
  chmod 0600 "$FRP_TLS_DIR/ca.key"
  chown root:root "$FRP_TLS_DIR/ca.key"
fi
chmod 0640 "$FRP_TLS_DIR/server.key"
chmod 0644 "$FRP_TLS_DIR"/*.crt
chown root:frp "$FRP_TLS_DIR/server.key" "$FRP_TLS_DIR"/*.crt

FRP_TOKEN="$(cat /etc/hermes-rdp/frp-token)"
cat > /etc/frp/frps.toml <<EOF
bindPort = $FRP_PORT
auth.method = "token"
auth.token = "$FRP_TOKEN"
transport.tls.force = true
transport.tls.certFile = "$FRP_TLS_DIR/server.crt"
transport.tls.keyFile = "$FRP_TLS_DIR/server.key"
allowPorts = [
  { start = $PORT_START, end = $PORT_END }
]
EOF
chmod 0640 /etc/frp/frps.toml
chown root:frp /etc/frp/frps.toml

cat > /etc/hermes-rdp/config.json <<EOF
{
  "public_host": "$HOST",
  "api_port": $API_PORT,
  "frp_bind_port": $FRP_PORT,
  "port_start": $PORT_START,
  "port_end": $PORT_END,
  "telegram_chat_id": "$TELEGRAM_CHAT_ID",
  "client_installer_url": "https://raw.githubusercontent.com/$REPO/$REF/scripts/install-client.ps1"
}
EOF
chmod 0640 /etc/hermes-rdp/config.json
chown root:hermes-rdp /etc/hermes-rdp/config.json

install -m 0644 "$SOURCE_ROOT/server/systemd/frps.service" /etc/systemd/system/frps.service
install -m 0644 "$SOURCE_ROOT/server/systemd/hermes-rdp.service" /etc/systemd/system/hermes-rdp.service

ufw allow "$FRP_PORT/tcp" comment 'Hermes RDP FRP' >/dev/null || true
ufw allow "$API_PORT/tcp" comment 'Hermes RDP API' >/dev/null || true
ufw allow "$PORT_START:$PORT_END/tcp" comment 'Hermes RDP devices' >/dev/null || true

systemctl daemon-reload
systemctl enable frps.service hermes-rdp.service
systemctl restart frps.service hermes-rdp.service
sleep 3

PYTHONPATH=/opt/hermes-rdp/app python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp

echo
echo "=== HERMES RDP INSTALLED ==="
echo "backup=$BACKUP_DIR"
echo "api=https://$HOST:$API_PORT"
echo "api_fingerprint=$(cat "$API_TLS_DIR/api.sha256")"
echo "frp_port=$FRP_PORT"
echo "rdp_ports=$PORT_START-$PORT_END"
echo "frps=$(systemctl is-active frps.service)"
echo "controller=$(systemctl is-active hermes-rdp.service)"
echo
echo "Create the first PC code while preserving port $PORT_START:"
echo "  sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port $PORT_START"
echo
echo "Then send /start to the Telegram bot."
