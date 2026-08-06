# Hermes RDP

Самостоятельный RDP-шлюз для нескольких Windows-компьютеров через один публичный Linux-сервер.

Сервер является единственным специальным узлом. **Основной ПК и дополнительные ПК устанавливаются одним и тем же Windows-клиентом** и отличаются только названием и автоматически выданным портом.

## Что умеет

- постоянные адреса вида `SERVER:53389`, `SERVER:53390`, `SERVER:53391`;
- один Telegram dashboard без простыни сообщений;
- список всех компьютеров и их ONLINE/OFFLINE-состояние;
- ON, OFF и RESTART выбранного RDP-туннеля;
- LIVE-метрики Windows каждые 3 секунды;
- CPU, RAM, диск, сеть, аптайм, процессы, пользователь и RDP-сессии;
- одноразовые коды подключения;
- автоматическая установка FRP и проверка SHA-256;
- одинаковая установка первого и последующих ПК;
- резервные копии, обновление, диагностика и удаление.

## Архитектура

```text
Windows PC 1 ─┐
Windows PC 2 ─┼─ FRPC + HTTPS agent ──> Hermes server ──> Telegram bot
Windows PC N ─┘                         FRPS + API + registry
```

- `frps` на сервере работает постоянно;
- каждый Windows-клиент получает уникальный `device_id`, API-токен и RDP-порт;
- ON/OFF управляет только выбранным клиентом;
- первый компьютер не имеет особого кода или отдельной роли.

Подробности: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Быстрый старт

### 1. Установка сервера

Ubuntu/Debian, команда выполняется через SSH на сервере:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install-server.sh   | sudo bash -s --       --host 31.76.77.87       --telegram-token 'TELEGRAM_BOT_TOKEN'       --telegram-chat-id 'TELEGRAM_USER_ID'       --migrate
```

Установщик:

- создаст резервную копию текущей конфигурации;
- установит FRP `0.70.1`;
- поднимет HTTPS API на `7443/tcp`;
- поднимет FRP control на `7000/tcp`;
- разрешит RDP-порты `53389–53420/tcp`;
- установит Telegram Multi-PC dashboard.

### 2. Подключение «Домашнего ПК» с сохранением `53389`

На сервере:

```bash
sudo hermes-rdpctl pair create --name 'Домашний ПК' --port 53389
```

Команда покажет `PAIR_CODE`, адрес и fingerprint. На Windows открой PowerShell **от администратора**:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install-client.ps1'
& ([scriptblock]::Create((irm $u))) -Server '31.76.77.87' -PairCode 'КОД' -Fingerprint 'FINGERPRINT'
```

### 3. Добавление следующих ПК

В Telegram нажми `➕ ДОБАВИТЬ ПК`. Бот создаст код и готовую PowerShell-команду. Запусти её на новом компьютере от администратора.

Новый ПК автоматически получит следующий свободный адрес, например:

```text
Домашний ПК → 31.76.77.87:53389
Ноутбук     → 31.76.77.87:53390
Офисный ПК  → 31.76.77.87:53391
```

## Управление

На сервере:

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Ноутбук'
sudo journalctl -u hermes-rdp.service -f
sudo journalctl -u frps.service -f
```

На Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDPgent.log' -Tail 50
```

## Обновление

Сервер:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/update-server.sh | sudo bash
```

Windows-клиент, PowerShell от администратора:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/main/scripts/update-client.ps1'
& ([scriptblock]::Create((irm $u)))
```

## Документация

- [Установка сервера](docs/INSTALL_SERVER.md)
- [Установка Windows-клиента](docs/INSTALL_WINDOWS.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Эксплуатация](docs/OPERATIONS.md)
- [Безопасность](docs/SECURITY.md)
- [Диагностика](docs/TROUBLESHOOTING.md)

## Требования

Сервер:

- Ubuntu или Debian;
- публичный IPv4 или DNS-имя;
- root/sudo;
- открытые TCP-порты `7000`, `7443` и диапазон RDP.

Клиент:

- Windows 10/11 Pro, Enterprise или Education;
- PowerShell 5.1+;
- права администратора;
- включённый входящий RDP.

## Важное ограничение v0.1

API-токен уникален для каждого устройства, но FRP использует общий серверный token. Отзыв устройства сразу закрывает его управление и телеметрию, однако при компрометации локальной FRP-конфигурации рекомендуется ротировать общий FRP token на сервере и переподключить доверенные устройства.

## Лицензия

MIT.
