# Hermes RDP

<p align="center">
  <strong>Self-hosted multi-PC RDP gateway через один публичный Linux-сервер с управлением из Telegram.</strong>
</p>

<p align="center">
  <a href="https://github.com/bakunity/RDP/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/bakunity/RDP?display_name=tag"></a>
  <a href="https://github.com/bakunity/RDP/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/bakunity/RDP/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
  <a href="docs/ARCHITECTURE.md"><img alt="OpenSSH" src="https://img.shields.io/badge/transport-OpenSSH-2ea44f"></a>
  <a href="docs/INSTALL_WINDOWS.md"><img alt="Windows" src="https://img.shields.io/badge/client-Windows%2010%2F11%20%7C%20Server%202019-blue"></a>
  <a href="docs/INSTALL_SERVER.md"><img alt="Linux" src="https://img.shields.io/badge/server-Debian%20%7C%20Ubuntu-orange"></a>
</p>

<p align="center">
  <a href="https://hermes-rdp.vercel.app/">Сайт</a> ·
  <a href="https://github.com/bakunity/RDP/releases/latest">Релизы</a> ·
  <a href="docs/INDEX.md">Документация</a> ·
  <a href="docs/SECURITY.md">Безопасность</a> ·
  <a href="docs/VALIDATED_SCENARIOS.md">Проверенные сценарии</a>
</p>

Hermes RDP публикует RDP нескольких Windows-компьютеров через один Linux-сервер с публичным IP или DNS. Каждый Windows-ПК сам поднимает исходящий reverse OpenSSH-туннель, получает постоянный внешний endpoint и управляется из одного Telegram dashboard.

На домашнем или офисном роутере Windows-ПК не требуется пробрасывать входящий RDP-порт: соединение к Hermes инициирует сам Windows-клиент.

> **Главный принцип проекта:** все Windows-компьютеры равноправны. Для каждого используется один и тот же installer и один и тот же Hermes Agent. Специальным узлом является только Linux-сервер Hermes.

## Что умеет Hermes RDP

- несколько независимых Windows-ПК через один сервер;
- постоянные endpoints вида `SERVER:53389`, `SERVER:53390`, `SERVER:53391`;
- стандартный Microsoft Remote Desktop без отдельного RDP-клиента Hermes;
- системный Microsoft OpenSSH вместо стороннего `frpc.exe`;
- отдельный Ed25519 keypair, API-token и порт для каждого устройства;
- Telegram `ON`, `OFF`, `RESTART`, удаление и LIVE-состояние каждого ПК;
- автоматический reconnect после сетевых сбоев и перезагрузок;
- Windows 10/11 и Windows Server support;
- transactional server/client update с backup и automatic rollback;
- отдельный Repair существующего клиента без повторного pairing и смены identity/порта;
- работа без Defender exclusions и без отключения Microsoft Defender.

## Схема

```text
┌────────────────────────┐
│ Windows: Домашний ПК   │──┐
│ RDP :3389              │  │
│ Hermes Agent + ssh.exe │  │
└────────────────────────┘  │
                            │ reverse OpenSSH :7000
┌────────────────────────┐  ├───────────────────────────┐
│ Windows: Ноутбук       │──┤                           │
│ Hermes Agent + ssh.exe │  │                           ▼
└────────────────────────┘  │              ┌─────────────────────────┐
                            │ HTTPS :7443  │ Hermes Linux server     │
┌────────────────────────┐  ├─────────────▶│ dedicated sshd          │
│ Windows: Офисный ПК    │──┘              │ API + Telegram + SQLite │
│ Hermes Agent + ssh.exe │                 └───────────┬─────────────┘
└────────────────────────┘                             │
                                                       ▼
                                                 Telegram owner

Microsoft RDP client
  ├── SERVER:53389 ── reverse SSH ──> Домашний ПК :3389
  ├── SERVER:53390 ── reverse SSH ──> Ноутбук     :3389
  └── SERVER:53391 ── reverse SSH ──> Офисный ПК  :3389
```

## Компоненты

| Компонент | Назначение |
|---|---|
| `hermes-rdp-sshd.service` | отдельный OpenSSH daemon для reverse-туннелей |
| `hermes-rdp.service` | HTTPS API, Telegram controller и registry |
| SQLite | устройства, pairing, команды, telemetry, token hashes и public keys |
| Windows OpenSSH Client | встроенные `ssh.exe` и `ssh-keygen.exe` |
| `HermesRdpAgent.ps1` | туннель, heartbeat, telemetry и управление доступом |

Hermes tunnel sshd отделён от административного SSH сервера. Tunnel-user не получает обычный shell/SFTP/PTY, а `permitlisten` ограничивает каждый device key только назначенным RDP endpoint.

Приватный Ed25519-ключ создаётся локально на Windows и не передаётся серверу.

## Telegram dashboard

Для нового компьютера используется **➕ ДОБАВИТЬ ПК**. Pairing-код одноразовый; если он истёк или уже использован, кнопка **🔁 НОВЫЙ КОД** создаёт новый код и обновляет installer command.

Карточка существующего ПК показывает состояние агента, доступ, SSH transport, публичный endpoint и telemetry. Действия применяются только к выбранному устройству:

```text
🟢 ON / 🔴 OFF          включить или отключить RDP access
🔄 RESTART              пересоздать Hermes SSH transport
🛠 ВОССТАНОВИТЬ КЛИЕНТ  восстановить existing Windows client
🗑 DELETE                отозвать устройство и освободить endpoint
```

Fresh pairing и Repair намеренно разделены. Repair не создаёт новый Device ID и не выполняет повторную регистрацию.

## Порты по умолчанию

| Назначение | Порт |
|---|---:|
| OpenSSH tunnel | `7000/tcp` |
| HTTPS API | `7443/tcp` |
| RDP endpoints | `53389–53420/tcp` |

Стандартный пул содержит 32 endpoint и расширяется параметрами server installer.

## Требования

**Server:** Debian/Ubuntu, Python 3.11+, systemd, OpenSSH Server, root/sudo, публичный IPv4 или DNS и доступ к GitHub/Telegram API.

**Windows:** Windows 10/11 Pro, Enterprise или Education x64 либо поддерживаемый Windows Server, Windows PowerShell 5.1+, локальный Administrator и Microsoft OpenSSH Client.

Windows Home не является штатным RDP host и не поддерживается.

## Быстрый старт v1.2.1

### 1. Установить сервер

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.2.1/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=v1.2.1 bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

Проверка:

```bash
sudo hermes-rdpctl doctor
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
```

### 2. Добавить Windows-ПК

1. Отправьте `/start` Telegram-боту.
2. Нажмите **➕ ДОБАВИТЬ ПК**.
3. Откройте PowerShell от имени администратора.
4. Скопируйте команду из Telegram целиком.
5. Введите понятное название компьютера.
6. Дождитесь `=== ГОТОВО ===`.

### 3. Подключиться

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

Первый свободный endpoint обычно начинается с `53389`, следующий получает `53390` и так далее.

## Обновление

Server:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.2.1/scripts/update-server.sh -o /tmp/update-hermes-rdp.sh
sudo env HERMES_RDP_REF=v1.2.1 bash /tmp/update-hermes-rdp.sh
rm -f /tmp/update-hermes-rdp.sh
```

Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.2.1/scripts/update-client.ps1'
$s=(irm $u).TrimStart([char]0xFEFF)
& ([scriptblock]::Create($s)) -RepositoryRef 'v1.2.1'
```

Оба updater-а сохраняют рабочее состояние до runtime mutation и имеют автоматический rollback при ошибке после изменения.

## Repair

Для уже зарегистрированного компьютера откройте его карточку в Telegram и нажмите **🛠 ВОССТАНОВИТЬ КЛИЕНТ**.

Repair может восстановить Hermes Agent и Scheduled Task, сохраняя существующие Device ID, API-token, Ed25519 keypair, `known_hosts` и назначенный RDP-порт.

Если потеряны `device.json`, private key или `known_hosts`, обычный Repair намеренно останавливается без автоматического re-pair/rekey.

## Безопасность

- HTTPS API использует TLS и certificate fingerprint pinning;
- SSH host key получается через уже pinned API и закрепляется в отдельном `known_hosts`;
- `StrictHostKeyChecking=yes`;
- каждый Windows-ПК имеет отдельный Ed25519 keypair;
- private SSH key остаётся на Windows;
- `permitlisten` ограничивает device key одним назначенным endpoint;
- у каждого устройства отдельный API-token, сервер хранит только hash;
- Telegram control ограничен заданным owner user/chat ID;
- admin SSH `:22` и Hermes tunnel sshd `:7000` разделены;
- Hermes не добавляет Defender exclusions.

**RDP boundary:** Hermes защищает регистрацию, control plane и tunnel, но конечный endpoint остаётся Windows RDP listener. Используйте сильные Windows credentials, NLA, обновления ОС и firewall restrictions там, где это возможно.

Подробнее: [docs/SECURITY.md](docs/SECURITY.md).

## Что проверено

В реальной эксплуатации подтверждены multi-device endpoints, внешний RDP, Windows/Linux reboot recovery, `OFF/ON/RESTART`, Windows 10 x64 из 32-bit PowerShell через Sysnative, Windows Server 2019, Microsoft Defender real-time protection, delete/revocation/port reuse, updater success/rollback и Repair success/rollback.

Полный acceptance без secret material: [docs/VALIDATED_SCENARIOS.md](docs/VALIDATED_SCENARIOS.md).

## Основные команды

Hermes server:

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Office-PC'
sudo hermes-rdpctl devices rename DEVICE_ID 'New name'
sudo hermes-rdpctl devices delete DEVICE_ID
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
```

Windows diagnostics:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
Get-Process ssh -ErrorAction SilentlyContinue
```

## Документация

| Документ | Для чего |
|---|---|
| [Быстрый старт](docs/QUICKSTART.md) | Развернуть Hermes и подключить первый ПК |
| [Установка сервера](docs/INSTALL_SERVER.md) | Server setup, порты и параметры |
| [Установка Windows](docs/INSTALL_WINDOWS.md) | Fresh pairing и Windows compatibility |
| [Архитектура](docs/ARCHITECTURE.md) | Компоненты и data flow |
| [API](docs/API.md) | Pairing, telemetry и command contracts |
| [Эксплуатация](docs/OPERATIONS.md) | Backup, update, delete и recovery |
| [Диагностика](docs/TROUBLESHOOTING.md) | Поиск проблем по симптомам |
| [Безопасность](docs/SECURITY.md) | TLS, identity, SSH restrictions и RDP boundary |
| [Проверенные сценарии](docs/VALIDATED_SCENARIOS.md) | Реально пройденный acceptance |
| [Тестирование от А до Я](docs/TESTING_A_TO_Z.md) | Полная процедура проверки |
| [Разработка](docs/DEVELOPMENT.md) | Структура проекта и developer rules |
| [Релизный процесс](docs/RELEASE.md) | Versioning, CI и GitHub Release |

Полный индекс: [docs/INDEX.md](docs/INDEX.md).

## Релизы

- [Последний релиз](https://github.com/bakunity/RDP/releases/latest)
- [Hermes RDP v1.2.1](https://github.com/bakunity/RDP/releases/tag/v1.2.1)
- [Release notes v1.2.1](docs/releases/v1.2.1.md)
- [Предыдущий v1.2.0](https://github.com/bakunity/RDP/releases/tag/v1.2.0)
- [История изменений](CHANGELOG.md)

Для production используйте конкретный release tag или другой заранее проверенный immutable ref. `main` предназначен для дальнейшей разработки.

## Лицензия

[MIT](LICENSE).
