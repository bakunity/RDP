# Безопасность Hermes RDP

Документ описывает модель угроз v1.0.0, реализованные меры и известные ограничения.

## Что защищаем

Секреты и чувствительные данные:

- Telegram bot token;
- разрешённый Telegram user ID;
- общий FRP token;
- FRP CA private key и server private key;
- HTTPS API private key;
- device API tokens;
- Windows `device.json` и `frpc.toml`;
- SQLite registry и backups;
- RDP credentials пользователей Windows.

Проект не хранит и не передаёт пароль Windows/RDP. Аутентификация RDP остаётся штатной функцией Windows.

## Модель доверия

```text
Telegram user ID
  → Telegram bot
  → server Registry
  → authenticated device polling
  → local FRPC action
```

Регистрация:

```text
trusted Telegram/CLI output
  → one-time pair code + API certificate fingerprint
  → pinned HTTPS pairing
  → unique device token + assigned RDP port
```

## Реализованные меры

### Telegram

- принимается только заданный `telegram_chat_id`;
- проверяются и chat ID, и actor ID;
- callback постороннего пользователя получает отказ;
- bot token хранится отдельным файлом с mode `0640`.

### Pairing

- код состоит из 8 символов без неоднозначных знаков;
- код генерируется `secrets.choice`;
- в SQLite хранится только SHA-256 кода;
- код одноразовый;
- TTL по умолчанию 900 секунд;
- preferred port проверяется на допустимый диапазон и занятость.

### Device API

- у каждого ПК отдельный `secrets.token_urlsafe(40)`;
- сервер хранит только SHA-256 token;
- сравнение выполняется через `secrets.compare_digest`;
- revoked device не проходит authentication;
- request body ограничен 128 KiB;
- SQL выполняется параметризованными запросами.

### TLS API

- минимум TLS 1.2;
- Windows installer и agent сверяют точный SHA-256 certificate fingerprint;
- fingerprint передаётся через Telegram/CLI, а не берётся из непроверенного API;
- проверку нельзя заменять `-SkipCertificateCheck` или глобальным отключением TLS validation.

### FRP

- `transport.tls.force = true` на server;
- Windows client проверяет собственную FRP CA;
- remote ports ограничены `allowPorts`;
- binary archives FRP закреплены на версии `0.70.1`;
- SHA-256 архивов проверяется до установки.

### Windows

- agent запускается от `SYSTEM`;
- `device.json` и `frpc.toml` имеют protected ACL;
- secrets доступны `SYSTEM` и Administrators;
- дополнительный входящий control/API port на Windows не открывается;
- команды приходят через исходящий HTTPS polling;
- agent не изменяет пароль или политику аутентификации Windows.

### Linux

- `frps.service` запускается от отдельного пользователя `frp`;
- `hermes-rdp.service` запускается от отдельного пользователя `hermes-rdp`;
- secret files принадлежат root и нужной service group;
- TLS private keys имеют ограниченные permissions;
- systemd units включают hardening-настройки;
- backup создаётся до миграции/обновления.

## Публичные порты

| Порт | Риск | Мера |
|---|---|---|
| `7000/tcp` | попытки FRP auth | token + forced TLS |
| `7443/tcp` | pairing/API abuse | TLS pinning, one-time code, bearer token |
| RDP range | brute force Windows login | Windows NLA/account policy/firewall |

RDP endpoints публичны. Это не заменяет сильный пароль Windows, NLA, lockout policy и своевременные обновления ОС.

## Главное ограничение v1: общий FRP token

API token персональный, но FRP token общий для всех клиентов. Если злоумышленник получил `frpc.toml` одного ПК, удаление device из Registry:

- блокирует telemetry и команды;
- скрывает устройство из активного dashboard;
- освобождает port для новой регистрации;
- **не делает украденный общий FRP token недействительным**.

Полный отзыв требует ротации token.

## Ротация FRP token

Подготовь окно обслуживания: все tunnels временно переподключатся.

На Hermes создать новый token:

```bash
sudo sh -c "openssl rand -base64 48 | tr -d '\n' > /etc/hermes-rdp/frp-token.new"
```

Не переключай server, пока новые configs не подготовлены на доверенных ПК.

На каждом доверенном Windows-компьютере обнови `auth.token` в `frpc.toml` через защищённый административный канал. Не отправляй token обычным сообщением.

Затем на Hermes:

```bash
sudo install -m 0640 -o root -g hermes-rdp /etc/hermes-rdp/frp-token.new /etc/hermes-rdp/frp-token
```

Обновить `/etc/frp/frps.toml`, перезапустить FRPS и Windows agents. После проверки удалить временный файл.

В будущем предпочтительное улучшение — per-device FRP auth/plugin или отдельная mTLS identity каждого клиента.

## Компрометация device token

1. определить `DEVICE_ID`;
2. выполнить `sudo hermes-rdpctl devices delete DEVICE_ID`;
3. остановить и удалить client на Windows;
4. проверить server logs;
5. создать новый pair code и зарегистрировать ПК заново;
6. при утечке `frpc.toml` также ротировать общий FRP token.

## Компрометация Telegram token

1. отозвать token через BotFather;
2. создать новый;
3. заменить `/etc/hermes-rdp/telegram-token`;
4. проверить owner/mode;
5. перезапустить `hermes-rdp.service`;
6. проверить, что разрешённый Telegram ID не менялся.

## Компрометация API TLS key

1. остановить `hermes-rdp.service`;
2. заменить API certificate/key;
3. пересчитать `api.sha256`;
4. перезапустить service;
5. обновить fingerprint на всех клиентах или перерегистрировать их;
6. считать старый fingerprint недоверенным.

## Backups

Backups содержат secrets и должны храниться как production credentials.

Минимум:

- owner root;
- mode `0700` для backup directory;
- шифрование при переносе вне сервера;
- отсутствие публичных ссылок;
- контролируемый retention;
- проверяемое уничтожение старых copies.

## Logging

В logs допустимы:

- device ID;
- display/machine name;
- endpoint port;
- error class/message без secrets;
- command action/sequence.

Нельзя логировать:

- Telegram token;
- pair code в server journal после выдачи;
- plaintext device token;
- FRP token;
- private keys;
- полный pairing response;
- содержимое `device.json`/`frpc.toml`.

## Reporting

Не создавай публичный GitHub issue с действующими secrets. Используй private security report владельцу репозитория и сразу отзывай скомпрометированные credentials.

Top-level policy: [../SECURITY.md](../SECURITY.md).

## Security roadmap

- per-device FRP authentication;
- automatic credential rotation;
- optional IP allowlists для RDP endpoints;
- rate limiting для pairing/API;
- audit events отдельной таблицей;
- signed release manifests;
- automatic encrypted backups;
- optional WireGuard/private access mode вместо публичного RDP range.
