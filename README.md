# Hermes RDP

Hermes RDP — самостоятельный шлюз для удалённого подключения к нескольким Windows-компьютерам через один Linux-сервер. Начиная с `v1.1.0`, транспорт построен на системном OpenSSH: сторонний `frpc.exe` больше не используется.

## Как это работает

```text
Windows 1 -- ssh -R --> SERVER:53389 --> 127.0.0.1:3389
Windows 2 -- ssh -R --> SERVER:53390 --> 127.0.0.1:3389
Windows 3 -- ssh -R --> SERVER:53391 --> 127.0.0.1:3389
```

Каждое устройство получает отдельные:

- Ed25519-ключ, создаваемый локально на Windows;
- постоянный внешний RDP-порт;
- API-токен и запись в Telegram;
- задачу автозапуска `Hermes RDP Agent`.

Приватный SSH-ключ не передаётся серверу. Сервер хранит только public key и разрешает ему слушать только назначенный порт.

## Компоненты

- `hermes-rdp-sshd.service` — отдельный OpenSSH daemon для reverse-туннелей;
- `hermes-rdp.service` — HTTPS API и Telegram dashboard;
- SQLite — устройства, pairing-коды, телеметрия и команды;
- Windows OpenSSH Client — встроенный `ssh.exe` и `ssh-keygen.exe`;
- PowerShell-агент — поддержание туннеля, телеметрия, ON/OFF/RESTART.

## Порты по умолчанию

| Назначение | Порт |
|---|---:|
| OpenSSH-туннели | `7000/tcp` |
| HTTPS API | `7443/tcp` |
| RDP устройств | `53389–53420/tcp` |

Диапазон по умолчанию рассчитан на 32 устройства и расширяется параметрами установщика.

## Требования

Сервер: Debian/Ubuntu, root или sudo, systemd, OpenSSH Server, UFW.

Windows: Windows 10/11 Pro, Enterprise или Education, 64-bit, PowerShell 5.1+, права администратора. Windows Home не поддерживает входящие RDP-сессии штатными средствами.

## Установка сервера v1.1.0

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.1.0/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=v1.1.0 bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

Миграция с `v1.0.x`/FRP выполняется той же командой с `--migrate`. Старые устройства без SSH-ключей будут отозваны и должны пройти pairing заново.

## Добавление Windows-ПК

1. Отправь `/start` Telegram-боту.
2. Нажми `➕ ДОБАВИТЬ ПК`.
3. Открой PowerShell от имени администратора.
4. Скопируй единый блок из Telegram.
5. Введи удобное название компьютера.

Установщик проверяет TLS fingerprint API, получает SSH host key через закреплённый HTTPS-канал, генерирует локальный Ed25519-ключ и создаёт задачу автозапуска.

## Проверка

Сервер:

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
```

Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
Get-Process ssh -ErrorAction SilentlyContinue
```

Подключение:

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

## Безопасность

- отдельный `sshd` не предоставляет shell и SFTP;
- парольная аутентификация выключена;
- `MaxSessions 0` запрещает интерактивные сессии;
- `permitlisten` привязывает ключ к одному RDP-порту;
- удаление устройства отзывает API-токен и SSH public key;
- SSH host key и API-сертификат закрепляются на клиенте;
- Defender-исключения и сторонние туннельные бинарники не требуются.

## Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [Установка сервера](docs/INSTALL_SERVER.md)
- [Установка Windows](docs/INSTALL_WINDOWS.md)
- [Миграция с FRP](docs/MIGRATION.md)
- [Эксплуатация](docs/OPERATIONS.md)
- [Безопасность](docs/SECURITY.md)
- [Тестирование от А до Я](docs/TESTING_A_TO_Z.md)

## Релизы

- [Последний релиз](https://github.com/bakunity/RDP/releases/latest)
- [Hermes RDP v1.1.0](https://github.com/bakunity/RDP/releases/tag/v1.1.0)
- [Release notes v1.1.0](docs/releases/v1.1.0.md)
