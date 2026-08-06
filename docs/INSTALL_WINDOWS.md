# Установка Windows-клиента

Один и тот же клиент используется для первого, второго и любого следующего компьютера. В коде нет отдельного «основного ПК».

## Требования

- 64-битная Windows 10/11 Pro, Enterprise или Education;
- PowerShell 5.1+;
- запуск от имени администратора;
- исходящий доступ к GitHub;
- доступ к Hermes API и FRP control port;
- входящий RDP должен поддерживаться редакцией Windows.

Windows Home не поддерживает штатный входящий RDP и установщиком блокируется.

## Что выдаёт сервер

Для подключения нужны:

- публичный адрес Hermes;
- одноразовый `PAIR_CODE`;
- SHA-256 `FINGERPRINT` TLS-сертификата API;
- необязательное понятное название ПК.

Код можно получить:

- кнопкой `➕ ДОБАВИТЬ ПК` в Telegram;
- командой `sudo hermes-rdpctl pair create --name 'Название ПК'` на сервере.

## Установка стабильного релиза

Открой **Windows PowerShell от имени администратора**.

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.0/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER_IP_OR_DOMAIN' -PairCode 'PAIR_CODE' -Fingerprint 'FINGERPRINT' -Name 'Название ПК' -RepositoryRef 'v1.0.0'
```

Для текущего домашнего компьютера:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.0/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER_IP_OR_DOMAIN' -PairCode 'PAIR_CODE' -Fingerprint 'FINGERPRINT' -Name 'Windows-PC-01' -RepositoryRef 'v1.0.0'
```

Параметр `-Name` можно не указывать: установщик спросит название или использует имя Windows-компьютера.

## Параметры

```text
-Server         публичный IP или DNS Hermes
-PairCode       одноразовый код регистрации
-Fingerprint    SHA-256 fingerprint HTTPS API
-Name           название в Telegram
-ApiPort        порт API, по умолчанию 7443
-RepositoryRef  тег или ветка агента, для продакшена v1.0.0
```

## Что делает установщик

1. Проверяет права администратора.
2. Проверяет 64-битную клиентскую Windows и поддержку RDP.
3. Останавливает старые задачи Hermes FRPC/Monitor.
4. Создаёт backup старых файлов.
5. Проверяет TLS fingerprint API.
6. Использует одноразовый код и регистрирует устройство.
7. Получает `device_id`, device token, FRP token, CA и RDP-порт.
8. Скачивает FRP `0.70.1` и проверяет SHA-256.
9. Скачивает `HermesRdpAgent.ps1` из указанного тега.
10. Создаёт `device.json` и `frpc.toml`.
11. Включает входящий RDP и штатное правило Windows Firewall.
12. Создаёт Scheduled Task `Hermes RDP Agent` от `SYSTEM`.
13. Закрывает secrets ACL для `SYSTEM` и Administrators.
14. Запускает агент и показывает постоянный endpoint.

## Установленные файлы

```text
C:\ProgramData\HermesRDP\
├── frpc.exe
├── frpc.toml
├── frp-ca.crt
├── HermesRdpAgent.ps1
├── device.json
├── agent-state.json
├── agent.log
└── backups\
```

Назначение:

| Файл | Содержимое |
|---|---|
| `frpc.exe` | FRP client |
| `frpc.toml` | адрес Hermes, FRP credentials и персональный remote port |
| `frp-ca.crt` | CA для проверки TLS FRPS |
| `HermesRdpAgent.ps1` | телеметрия, команды и контроль FRPC |
| `device.json` | device ID, API token, endpoint и fingerprint |
| `agent-state.json` | локальное состояние ON/OFF и sequence команды |
| `agent.log` | журнал агента |

`device.json` и `frpc.toml` содержат секреты. Не отправляй их в чат, issue или репозиторий.

## Scheduled Task

Проверить:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
```

Запустить вручную:

```powershell
Start-ScheduledTask -TaskName 'Hermes RDP Agent'
```

Перезапустить:

```powershell
Stop-ScheduledTask -TaskName 'Hermes RDP Agent' -ErrorAction SilentlyContinue; Start-ScheduledTask -TaskName 'Hermes RDP Agent'
```

## Проверка после установки

Лог:

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

FRPC process:

```powershell
Get-Process frpc -ErrorAction SilentlyContinue
```

Локальный RDP:

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

Связь с Hermes:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 7000
```

API:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 7443
```

После первых данных Telegram должен показать устройство как `ONLINE` максимум через 15 секунд.

## Как работают ON/OFF/RESTART

- `ON` записывает локальное состояние `enabled=true` и запускает FRPC;
- `OFF` останавливает только FRPC выбранного ПК;
- `RESTART` перезапускает только FRPC выбранного ПК;
- агент продолжает работать и отправлять телеметрию, чтобы получить следующую команду;
- другие ПК не затрагиваются.

## Обновление

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.0/scripts/update-client.ps1'; & ([scriptblock]::Create((irm $u))) -RepositoryRef 'v1.0.0'
```

Скрипт сохраняет backup текущего `HermesRdpAgent.ps1`, проверяет синтаксис новой версии и только потом запускает задачу.

## Удаление

Сначала удали устройство в Telegram или на сервере:

```bash
sudo hermes-rdpctl devices delete DEVICE_ID
```

Затем на Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.0/scripts/uninstall-client.ps1'; & ([scriptblock]::Create((irm $u)))
```

Удаление локального клиента не удаляет Windows-пользователей и не меняет пароль RDP.

## Повторная регистрация

Pair code используется один раз. Для переустановки или переноса ПК:

1. удалить старое устройство из Telegram/CLI;
2. создать новый pair code;
3. снова запустить общий установщик.
