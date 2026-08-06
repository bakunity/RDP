# Установка сервера Hermes RDP

Сервер Hermes — единственный специальный узел системы. Он принимает FRP-туннели, обслуживает HTTPS API, хранит SQLite-реестр и управляет Telegram dashboard.

## Поддерживаемая среда

- Ubuntu или Debian;
- `systemd`;
- Python 3.11+;
- публичный IPv4 или DNS-имя;
- root или пользователь с `sudo`;
- исходящий доступ к GitHub и Telegram API.

## Публичные порты

По умолчанию:

| Порт | Назначение |
|---|---|
| `7000/tcp` | FRP control для всех Windows-клиентов |
| `7443/tcp` | HTTPS API регистрации, телеметрии и команд |
| `53389–53420/tcp` | постоянные публичные RDP endpoints |

Обычный SSH-порт сервера должен оставаться доступным отдельно.

## Подготовка Telegram

Нужны:

- bot token;
- числовой user ID владельца Telegram;
- бот не должен использоваться другим webhook/polling-приложением одновременно.

Token лучше не писать напрямую в историю shell:

```bash
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
```

## Стабильная установка v1.0.0

Скачать установщик:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.0/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
```

Проверить содержимое:

```bash
less /tmp/install-hermes-rdp.sh
```

### Новая установка

```bash
sudo env HERMES_RDP_REF=v1.0.0 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID
```

### Миграция старой установки

```bash
sudo env HERMES_RDP_REF=v1.0.0 bash /tmp/install-hermes-rdp.sh --host 31.76.77.87 --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID --migrate
```

После запуска:

```bash
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

## Параметры установщика

```text
--host HOST                 публичный IP или DNS
--telegram-token TOKEN      Telegram bot token
--telegram-chat-id ID       разрешённый Telegram user/chat ID
--api-port PORT             HTTPS API, по умолчанию 7443
--frp-port PORT             FRP control, по умолчанию 7000
--port-start PORT           первый RDP-порт, по умолчанию 53389
--port-end PORT             последний RDP-порт, по умолчанию 53420
--migrate                   подтвердить замену старого Hermes RDP bot/setup
```

Версия исходников выбирается переменной окружения `HERMES_RDP_REF`. Для продакшена указывай релизный тег, например `v1.0.0`. Для тестовой ветки можно временно передать имя ветки.

## Что делает установщик

1. Устанавливает системные зависимости.
2. Создаёт backup текущих файлов.
3. Создаёт системных пользователей `frp` и `hermes-rdp`.
4. Устанавливает серверный Python-код в `/opt/hermes-rdp/app`.
5. Устанавливает `hermes-rdpctl` в `/usr/local/bin`.
6. Скачивает FRP `0.70.1` и проверяет SHA-256.
7. Создаёт или импортирует FRP token.
8. Создаёт TLS-сертификат API и отдельную CA для FRP.
9. Создаёт `/etc/frp/frps.toml`.
10. Создаёт `/etc/hermes-rdp/config.json`.
11. Устанавливает `frps.service` и `hermes-rdp.service`.
12. Добавляет UFW-правила.
13. Включает и запускает службы.
14. Печатает fingerprint API и команду для первого ПК.

## Каталоги и файлы

```text
/etc/hermes-rdp/
├── config.json
├── telegram-token
├── frp-token
├── frp-ca.crt
└── tls/
    ├── api.crt
    ├── api.key
    └── api.sha256

/etc/frp/
├── frps.toml
└── tls/
    ├── ca.crt
    ├── ca.key
    ├── server.crt
    └── server.key

/opt/hermes-rdp/app/hermes_rdp/
/var/lib/hermes-rdp/state.sqlite3
/var/backups/hermes-rdp/
/usr/local/bin/hermes-rdpctl
```

## systemd

```bash
sudo systemctl status frps.service hermes-rdp.service --no-pager
```

```bash
sudo systemctl is-enabled frps.service hermes-rdp.service
```

```bash
sudo journalctl -u frps.service -n 100 --no-pager
```

```bash
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

`frps.service` работает постоянно. ON/OFF в Telegram не останавливает серверный FRPS: команда отправляется только выбранному Windows-клиенту.

## Проверка после установки

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo ss -lntp | grep -E ':(7000|7443)\b'
```

```bash
sudo ufw status numbered
```

Проверить API локально:

```bash
curl -k https://127.0.0.1:7443/healthz
```

Ожидается JSON с `"ok":true` и `"version":"1.0.0"`.

## Создание первого кода

С сохранением старого endpoint:

```bash
sudo hermes-rdpctl pair create --name 'Домашний ПК' --port 53389
```

Автоматический свободный порт:

```bash
sudo hermes-rdpctl pair create --name 'Ноутбук'
```

Своё время жизни кода, например 5 минут:

```bash
sudo hermes-rdpctl pair create --name 'Ноутбук' --ttl 300
```

## Backup

Перед изменениями создаётся каталог:

```text
/var/backups/hermes-rdp/<UTC_TIMESTAMP>
```

Символическая ссылка на последний установочный backup:

```text
/var/backups/hermes-rdp/latest
```

Не удаляй backup до полной проверки сервера, Telegram и первого Windows-клиента.

## Повторный запуск

Установщик рассчитан на контролируемую переустановку и создаёт новый backup. При обнаружении старого отдельного `hermes-rdp-bot.service` требуется явный `--migrate`.

## Следующий шаг

[Установка Windows-клиента](INSTALL_WINDOWS.md).
