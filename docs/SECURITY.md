# Безопасность

## Границы доступа

Выделенный OpenSSH daemon принимает только пользователя `hermes-tunnel`, только public-key authentication и только remote TCP forwarding. Shell, PTY, SFTP, agent forwarding, X11 и local forwarding выключены.

Каждый ключ получает `permitlisten` только для назначенного внешнего порта. Компрометация одного клиентского ключа не даёт административный SSH-доступ и не разрешает занять порт другого устройства.

## Закрепление идентичности

API использует SHA-256 certificate pinning. SSH host public key доставляется через уже закреплённый HTTPS-канал и сохраняется в отдельном `known_hosts`. Клиент запускается с `StrictHostKeyChecking=yes`.

## Секреты

- приватный Ed25519-ключ хранится только на Windows;
- сервер хранит public key;
- API-токены хранятся на сервере только как SHA-256 hash;
- Telegram token находится в отдельном root-owned файле.

## Отзыв

DELETE удаляет запись устройства, поэтому одновременно перестают работать API-токен и SSH public key. Текущий listener закрывается root-helper, ограниченным диапазоном Hermes-портов.
