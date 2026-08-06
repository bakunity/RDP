# Hermes RDP

**Hermes RDP** — self-hosted шлюз для доступа к нескольким Windows-компьютерам через один Linux-сервер. Начиная с `v1.1.0`, транспорт построен на системном OpenSSH: Windows использует встроенный `ssh.exe`, а сервер запускает отдельный изолированный `sshd`.

[Сайт](https://hermes-rdp.vercel.app/) · [Исходники](https://github.com/bakunity/RDP) · [Документация](docs/INDEX.md) · [Безопасность](docs/SECURITY.md)

## Что уже проверено

- чистая установка на Debian;
- Telegram pairing;
- регистрация Windows и генерация Ed25519-ключа;
- reverse SSH-туннель;
- внешний RDP-доступ через мобильную сеть;
- работа без `frpc.exe` и исключений Microsoft Defender.

Подробности: [проверенные сценарии](docs/VALIDATED_SCENARIOS.md).

## Схема

```text
Windows PC 1 -- ssh -R --> SERVER:53389 --> 127.0.0.1:3389
Windows PC 2 -- ssh -R --> SERVER:53390 --> 127.0.0.1:3389
Windows PC 3 -- ssh -R --> SERVER:53391 --> 127.0.0.1:3389
```

Каждый компьютер получает отдельные:

- Ed25519-ключ, создаваемый локально;
- постоянный RDP-порт;
- API-token;
- запись и управление в Telegram;
- задачу `Hermes RDP Agent` от имени `SYSTEM`.

Приватный ключ не передаётся серверу. Сервер хранит public key и разрешает ему слушать только назначенный порт через `permitlisten`.

## Компоненты

| Компонент | Назначение |
|---|---|
| `hermes-rdp-sshd.service` | отдельный OpenSSH daemon для reverse-туннелей |
| `hermes-rdp.service` | HTTPS API, Telegram bot и registry |
| SQLite | pairing-коды, устройства, команды и телеметрия |
| Windows OpenSSH Client | `ssh.exe` и `ssh-keygen.exe` |
| `HermesRdpAgent.ps1` | туннель, heartbeat, команды и LIVE-метрики |

## Порты по умолчанию

| Порт | Назначение |
|---:|---|
| `7000/tcp` | OpenSSH-туннели |
| `7443/tcp` | HTTPS API |
| `53389–53420/tcp` | внешние RDP endpoints |

Стандартный пул рассчитан на 32 устройства и расширяется параметрами установщика.

## Быстрый старт

### 1. Сервер

До публикации официального release tag используйте проверенный source ref из проекта, а не изменяемый `main`.

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/REF/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=REF bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

### 2. Проверка

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
```

### 3. Windows

Отправьте `/start` Telegram-боту, нажмите **➕ ДОБАВИТЬ ПК**, затем выполните готовую команду в PowerShell администратора. Успех подтверждается строкой `=== ГОТОВО ===`.

### 4. RDP

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

## Важная граница безопасности

Hermes защищает регистрацию, ключи и туннель, но конечный endpoint остаётся RDP-портом Windows. Используйте сильные уникальные пароли, обновляйте Windows, включайте NLA и ограничивайте источники через firewall там, где это возможно.

## Документация

- [Индекс по ролям](docs/INDEX.md)
- [Быстрый старт](docs/QUICKSTART.md)
- [Установка сервера](docs/INSTALL_SERVER.md)
- [Установка Windows](docs/INSTALL_WINDOWS.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Эксплуатация](docs/OPERATIONS.md)
- [Диагностика](docs/TROUBLESHOOTING.md)
- [Тестирование от А до Я](docs/TESTING_A_TO_Z.md)
- [Модель безопасности](docs/SECURITY.md)
- [Миграция с FRP](docs/MIGRATION.md)

## Состояние проверки

Основной внешний путь уже прошёл PASS. До полного acceptance остаются:

- второй Windows-ПК;
- восстановление после перезагрузки Windows;
- Telegram-команды `OFF`, `ON`, `RESTART`;
- удаление устройства и повторное использование освобождённого порта.

## Релизный статус

Код OpenSSH-версии `1.1.0` уже протестирован на фиксированном commit. [Официальный тег `v1.1.0`](https://github.com/bakunity/RDP/releases/tag/v1.1.0) ещё ожидает успешной публикации GitHub Release; до этого установка должна использовать проверенный immutable source ref.

Лицензия: [MIT](LICENSE).
