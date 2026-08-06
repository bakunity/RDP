# Установка сервера

## Поддерживаемая среда

Debian/Ubuntu, root или sudo, systemd, OpenSSH Server, UFW и Python 3.11+.

## Порты

- `22/tcp` — административный SSH сервера, установщик его не меняет;
- `7000/tcp` — отдельный Hermes OpenSSH daemon;
- `7443/tcp` — HTTPS API;
- `53389–53420/tcp` — RDP endpoints.

## Чистая установка

До публикации официального release tag используйте проверенный source ref.

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/REF/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=REF bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID \
  --api-port 7443 \
  --ssh-port 7000 \
  --port-start 53389 \
  --port-end 53420
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

## Что создаётся

- `/opt/hermes-rdp/app`;
- `/etc/hermes-rdp/config.json`;
- `/etc/hermes-rdp/tls/`;
- отдельный SSH host key;
- `/var/lib/hermes-rdp/state.sqlite3`;
- `hermes-rdp.service`;
- `hermes-rdp-sshd.service`;
- системные пользователи `hermes-rdp` и `hermes-tunnel`.

## Проверка

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
sudo /usr/sbin/sshd -t -f /etc/hermes-rdp/sshd_config
sudo ss -ltnp | grep -E ':(7000|7443)\b'
```

Ожидается:

```text
config: OK
api: OK (..., openssh)
ssh-tunnel: LISTEN 7000
api: LISTEN 7443
ssh-config: OK
```

До подключения первого ПК RDP-порты должны быть закрыты. Порт появляется только после успешного reverse-туннеля.

## Backup

Каждый запуск создаёт каталог в `/var/backups/hermes-rdp/`. Не удаляйте backup до прохождения внешнего RDP-теста.

## Повторная установка

Переход с `v1.0.x`/FRP требует явного `--migrate`. Чистой OpenSSH-установке этот флаг не нужен.

## После установки

1. Отправьте `/start` Telegram-боту.
2. Убедитесь, что панель показывает OpenSSH port `7000`.
3. Добавьте первый Windows-ПК.
4. Проверьте endpoint из другой сети.
