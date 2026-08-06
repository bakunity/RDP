# Установка сервера

## Новая установка

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.1.0/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=v1.1.0 bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID
unset TG_TOKEN
```

Параметры: `--api-port`, `--ssh-port`, `--port-start`, `--port-end`, `--migrate`.

Установщик создаёт backup, отдельного пользователя туннелей, выделенный SSH host key, ограниченный `sshd_config`, systemd-сервисы, UFW-правила и API TLS-сертификат.

## Проверка

```bash
sudo hermes-rdpctl doctor
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
sudo ss -lntp | grep -E ':7000|:7443'
```

Обычный административный SSH сервера не изменяется.
