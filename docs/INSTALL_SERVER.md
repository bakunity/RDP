# Установка сервера

## Перед началом

Подготовь:

- публичный IP или DNS сервера;
- Telegram bot token;
- свой числовой Telegram user ID;
- SSH-доступ с sudo.

## Новая установка

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install-server.sh   | sudo bash -s --       --host SERVER_IP_OR_DOMAIN       --telegram-token 'TOKEN'       --telegram-chat-id 'USER_ID'
```

## Миграция существующего Hermes

При обнаружении старого `hermes-rdp-bot.service` установщик остановится. Для подтверждённой миграции добавь `--migrate`.

Перед изменениями создаётся backup:

```text
/var/backups/hermes-rdp/<UTC_TIMESTAMP>
```

## Порты

По умолчанию:

- `7000/tcp` — FRP control;
- `7443/tcp` — HTTPS API;
- `53389–53420/tcp` — публичные RDP endpoints.

Диапазон можно изменить параметрами `--port-start` и `--port-end`.

## Первый компьютер

Чтобы сохранить старый порт:

```bash
sudo hermes-rdpctl pair create --name 'Домашний ПК' --port 53389
```

Первый клиент устанавливается тем же `install-client.ps1`, что и остальные.
