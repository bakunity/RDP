# Hermes RDP

<p align="center">
  <strong>Самостоятельный multi-PC RDP-шлюз через один публичный Linux-сервер с управлением из Telegram.</strong>
</p>

<p align="center">
  <a href="https://github.com/bakunity/RDP/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/bakunity/RDP?display_name=tag"></a>
  <a href="https://github.com/bakunity/RDP/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/bakunity/RDP/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <img alt="Windows" src="https://img.shields.io/badge/client-Windows%2010%2F11-blue">
  <img alt="Server" src="https://img.shields.io/badge/server-Ubuntu%20%7C%20Debian-orange">
</p>

Hermes RDP публикует RDP нескольких Windows-компьютеров через один сервер с публичным IP. Сервер принимает FRP-туннели, хранит реестр устройств, выдаёт постоянные порты и показывает состояние каждого ПК в одном Telegram-дашборде.

> **Главный принцип проекта:** основной компьютер и все дополнительные компьютеры равноправны. Для каждого используется один и тот же Windows-установщик и один и тот же агент. Специальным узлом является только сервер Hermes.

## Что входит в v1.0.3

- постоянные адреса вида `SERVER:53389`, `SERVER:53390`, `SERVER:53391`;
- единый Telegram dashboard без потока отдельных сообщений;
- список всех ПК и состояния `ONLINE` / `OFFLINE`;
- персональные `ON`, `OFF` и `RESTART` для каждого туннеля;
- LIVE-метрики Windows каждые 3 секунды;
- CPU, RAM, диск, сеть, аптайм, процессы, пользователь и RDP-сессии;
- одноразовые восьмисимвольные коды подключения;
- автоматическая выдача свободного RDP-порта;
- установка FRP `0.70.1` с проверкой SHA-256;
- TLS для API и FRP;
- резервные копии, обновление, удаление и диагностика;
- CI на Linux и Windows PowerShell 5.1.

## Схема

```text
┌──────────────────────┐
│ Windows: Windows-PC-01 │──┐
│ FRPC + RDP Agent     │  │
└──────────────────────┘  │
                           │  FRP control 7000/tcp
┌──────────────────────┐  ├──────────────────────────┐
│ Windows: Ноутбук     │──┤                          │
│ FRPC + RDP Agent     │  │                          ▼
└──────────────────────┘  │              ┌────────────────────────┐
                           │ HTTPS 7443    │ Hermes Linux server    │
┌──────────────────────┐  ├─────────────▶│ FRPS + API + SQLite    │
│ Windows: Офисный ПК  │──┘              │ Telegram dashboard     │
│ FRPC + RDP Agent     │                 └───────────┬────────────┘
└──────────────────────┘                              │
                                                      ▼
                                             Telegram пользователя
```

Публичные RDP endpoints:

```text
Windows-PC-01 → SERVER_IP_OR_DOMAIN:53389
Ноутбук     → SERVER_IP_OR_DOMAIN:53390
Офисный ПК  → SERVER_IP_OR_DOMAIN:53391
```

## Быстрый старт

### 1. Подготовить сервер

Требуется Ubuntu/Debian, публичный IP или DNS, `sudo`, Telegram bot token и числовой Telegram user ID.

Стабильный установщик последнего релиза:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.3/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
```

Чтобы Telegram token не попал в историю команд:

```bash
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
```

Новая установка:

```bash
sudo env HERMES_RDP_REF=v1.0.3 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID
```

Миграция уже работающего Hermes/FRP/Telegram-бота:

```bash
sudo env HERMES_RDP_REF=v1.0.3 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID --migrate
```

После установки:

```bash
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
sudo hermes-rdpctl doctor
```

### 2. Подключить текущий «Windows-PC-01» и сохранить порт `53389`

На Hermes:

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
```

Команда выведет:

```text
PAIR_CODE=XXXXXXXX
SERVER=SERVER_IP_OR_DOMAIN
FINGERPRINT=...
```

На Windows открой PowerShell **от имени администратора**:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.3/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER_IP_OR_DOMAIN' -PairCode 'PAIR_CODE' -Fingerprint 'FINGERPRINT' -Name 'Windows-PC-01' -RepositoryRef 'v1.0.3'
```

### 3. Добавить любой следующий ПК

В Telegram нажми `➕ ДОБАВИТЬ ПК`, скопируй команду и выполни её на новом компьютере от администратора. Все дополнительные ПК устанавливаются точно так же, как первый.

## Telegram-панель

Главный экран показывает список устройств:

```text
🖥 HERMES RDP · КОМПЬЮТЕРЫ

🟢 Windows-PC-01 · :53389
🟢 Ноутбук · :53390
🔴 Офисный ПК · :53391

➕ ДОБАВИТЬ ПК
🔄 REFRESH    ⏸ LIVE 3s
```

Экран устройства показывает ресурсы Windows, endpoint, FRPC, RDP-сессии и процессы. Кнопки `ON`, `OFF`, `RESTART` влияют только на выбранный ПК; `frps` на Hermes продолжает работать для остальных устройств.

## Основные команды

Hermes:

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Ноутбук'
sudo hermes-rdpctl devices rename DEVICE_ID 'Новое имя'
sudo hermes-rdpctl devices delete DEVICE_ID
sudo hermes-rdpctl dashboard reset
```

Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

## Обновление

Сервер до стабильной версии `v1.0.3`:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.3/scripts/update-server.sh -o /tmp/update-hermes-rdp.sh
sudo env HERMES_RDP_REF=v1.0.3 bash /tmp/update-hermes-rdp.sh
rm -f /tmp/update-hermes-rdp.sh
```

Windows-клиент:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.3/scripts/update-client.ps1'; & ([scriptblock]::Create((irm $u))) -RepositoryRef 'v1.0.3'
```

## Релизы

- [Последний релиз](https://github.com/bakunity/RDP/releases/latest)
- [Hermes RDP v1.0.3](https://github.com/bakunity/RDP/releases/tag/v1.0.3)
- [История изменений](CHANGELOG.md)
- [Описание релиза v1.0.3](docs/releases/v1.0.3.md)

Для продакшена используй URL с конкретным тегом. `main` предназначен для разработки и может изменяться между релизами.

## Документация

| Документ | Для чего |
|---|---|
| [Быстрый старт](docs/QUICKSTART.md) | Развернуть сервер и подключить первый ПК |
| [Тестирование от А до Я](docs/TESTING_A_TO_Z.md) | Полная проверка на отдельном сервере, новом боте и новом Windows-ПК |
| [Установка сервера](docs/INSTALL_SERVER.md) | Параметры, порты, файлы и проверка установки |
| [Установка Windows](docs/INSTALL_WINDOWS.md) | Подключение основного и дополнительных ПК |
| [Миграция](docs/MIGRATION.md) | Перевод старой одно-PC схемы без смены `53389` |
| [Архитектура](docs/ARCHITECTURE.md) | Компоненты, потоки данных и границы ответственности |
| [API](docs/API.md) | Контракты pairing, telemetry и command result |
| [Эксплуатация](docs/OPERATIONS.md) | Runbook, backup, restore, update и удаление |
| [Диагностика](docs/TROUBLESHOOTING.md) | Поиск проблем по симптомам |
| [Безопасность](docs/SECURITY.md) | Секреты, TLS, ACL и ограничения v1 |
| [Разработка](docs/DEVELOPMENT.md) | Структура проекта и правила для будущих разработчиков |
| [Релизы](docs/RELEASE.md) | Подготовка и автоматическая публикация версий |

Полный индекс: [docs/INDEX.md](docs/INDEX.md).

## Требования

**Сервер:** Ubuntu/Debian, Python 3.11+, публичный IPv4 или DNS, root/sudo, доступ к GitHub и Telegram API.

**Windows:** 64-битная Windows 10/11 Pro, Enterprise или Education, PowerShell 5.1+, права администратора, доступ к GitHub и Hermes, включённый входящий RDP.

## Безопасность

- API работает через TLS 1.2+ и pinning SHA-256 fingerprint;
- pairing code одноразовый и по умолчанию действует 15 минут;
- у каждого устройства отдельный API token, на сервере хранится только его SHA-256;
- FRP использует собственную CA и принудительный TLS;
- доступ к Telegram ограничен одним заданным user ID;
- локальные секреты Windows закрыты ACL для `SYSTEM` и Administrators.

Текущее ограничение: FRP token общий для всех клиентов. Подробности и процедура ротации: [docs/SECURITY.md](docs/SECURITY.md).

## Лицензия

[MIT](LICENSE).
