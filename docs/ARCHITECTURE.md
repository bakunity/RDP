# Архитектура Hermes RDP

## Общая схема

```text
Remote RDP client
        |
        | TCP SERVER:RDP_PORT
        v
Linux listener created by dedicated sshd
        |
        | reverse forwarding
        v
Windows 127.0.0.1:3389
```

Windows всегда инициирует исходящее SSH-соединение. Проброс портов на домашнем или офисном роутере Windows-ПК не требуется.

## Сервер

### `hermes-rdp-sshd.service`

Отдельный экземпляр OpenSSH на `7000/tcp`. Он не заменяет административный SSH сервера и использует собственные config, pid file и host key.

Ограничения tunnel-user:

- только public-key authentication;
- нет shell, PTY и SFTP;
- нет X11 и agent forwarding;
- нет local forwarding;
- remote forwarding ограничен назначенным endpoint;
- `AuthorizedKeysCommand` получает актуальный ключ из SQLite;
- `permitlisten` разрешает только конкретный RDP-порт.

### `hermes-rdp.service`

Запускает:

- HTTPS API;
- Telegram controller;
- SQLite registry;
- pairing;
- telemetry и heartbeat;
- очередь команд устройствам.

### SQLite

Хранит:

- устройства и назначенные порты;
- хэши API-token;
- SSH public keys;
- pairing-коды;
- команды;
- настройки Telegram;
- последнюю телеметрию.

## Windows

`HermesRdpAgent.ps1` работает через Scheduled Task от имени `SYSTEM` и поддерживает:

- `ssh.exe -N -R`;
- reconnect и backoff;
- heartbeat и telemetry;
- команды `ON`, `OFF`, `RESTART`;
- проверку endpoint status.

Приватный Ed25519-ключ остаётся в `C:\ProgramData\HermesRDP` с ACL только для `SYSTEM` и Administrators.

## Trust chain

1. Пользователь получает API fingerprint через доверенный канал установки.
2. Установщик закрепляет SHA-256 сертификата HTTPS API.
3. Через закреплённый API клиент получает SSH host key.
4. SSH использует отдельный `known_hosts` и `StrictHostKeyChecking=yes`.
5. Сервер принимает public key только для назначенного порта.

## Жизненный цикл устройства

1. Telegram создаёт одноразовый pairing-код.
2. Windows локально генерирует keypair.
3. API проверяет код и public key.
4. Registry выдаёт постоянный RDP-порт и device token.
5. Agent запускает reverse SSH.
6. Устройство появляется ONLINE после heartbeat.

## Удаление устройства

DELETE:

- отзывает API-token;
- отзывает SSH public key;
- закрывает listener;
- освобождает порт;
- не удаляет локальные файлы Windows автоматически.

Локальная очистка выполняется отдельным uninstall-скриптом.

## Масштабирование

Стандартный пул `53389–53420` даёт 32 одновременных endpoint. Диапазон можно расширить, но нужно учитывать firewall, мониторинг, лимиты сервера и модель доступа к открытым RDP-портам.
