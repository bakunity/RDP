# Миграция с FRP на OpenSSH

`v1.1.0` заменяет FRP полностью. Миграция требует повторного pairing Windows-устройств, потому что у старых записей нет индивидуальных SSH public keys.

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.1.0/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=v1.1.0 bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID \
  --migrate
unset TG_TOKEN
```

Установщик:

- создаёт backup в `/var/backups/hermes-rdp/`;
- останавливает и удаляет `frps.service`;
- поднимает `hermes-rdp-sshd.service` на прежнем control-порту;
- удаляет legacy-записи без SSH-ключей;
- сохраняет Telegram, API TLS и диапазон RDP-портов.

После миграции добавь каждый Windows-ПК заново через Telegram. Исключения Defender для FRP можно удалить после проверки, что старый `frpc.exe` больше не используется.
