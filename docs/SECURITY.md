# Модель безопасности Hermes RDP

## Защищаемые активы

- Telegram bot token;
- API certificate private key;
- Windows Ed25519 private keys;
- device API-tokens;
- pairing-коды;
- Windows credentials;
- SQLite registry.

## Серверные границы

Hermes использует отдельный `sshd`, не изменяя административный SSH на порту `22`.

Tunnel-user не получает:

- shell;
- PTY;
- SFTP;
- local forwarding;
- agent forwarding;
- X11 forwarding;
- произвольный remote port.

`AuthorizedKeysCommand` выдаёт ключ с ограничениями, а `permitlisten` привязывает его к назначенному RDP-порту.

## Клиентская trust chain

1. HTTPS API проверяется по SHA-256 fingerprint.
2. SSH host key приходит через уже закреплённый API.
3. `StrictHostKeyChecking` запрещает незаметную замену сервера.
4. Private key остаётся на Windows.
5. Secret files получают ACL только для `SYSTEM` и Administrators.

## Pairing

Код одноразовый и ограничен по времени. Device создаётся после проверки структуры Ed25519 public key.

При ошибке после pairing установщик пытается отозвать созданное устройство, чтобы не оставлять активный key и занятый порт.

## Telegram

Контроллер сверяет chat ID и actor ID. Bot token хранится в root-owned файле и не должен попадать в команды, логи, скриншоты или git.

## RDP boundary

Hermes защищает регистрацию, ключи и путь до Windows, но не заменяет безопасность самой RDP-сессии.

Внешний endpoint доступен как TCP-порт сервера. Обязательны:

- сильный уникальный Windows-пароль;
- NLA;
- актуальные обновления Windows;
- минимальное число администраторов;
- ограничение source IP или дополнительный сетевой контроль, когда сценарий это допускает;
- мониторинг неудачных входов.

Не используйте пустые пароли или общие пароли между устройствами.

## Отзыв

DELETE должен:

- отозвать API-token;
- отозвать SSH public key;
- завершить listener;
- освободить порт.

Украденный старый key после отзыва не должен аутентифицироваться.

## Backup и restore

Backup содержит чувствительные данные. Храните его с mode `0700`, не загружайте в публичные облака без шифрования и не прикладывайте к issue.

После restore проверьте permissions, `doctor`, SSH host key и существующие устройства.

## Что не публиковать

Не публикуйте:

- bot token;
- pairing-код;
- TLS fingerprint вместе с готовой командой установки;
- private key;
- `device.json`;
- полный agent log;
- реальные IP и Telegram IDs из production без необходимости.

## Сообщение об уязвимости

Используйте процедуру из [корневого SECURITY.md](../SECURITY.md). Не публикуйте рабочий exploit или секреты в открытом issue.
