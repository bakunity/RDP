# Быстрый старт

Этот сценарий подходит и для новой установки, и для перевода текущей одно-PC схемы в Hermes RDP v1.0.4.

## Результат

После выполнения шагов:

- Hermes постоянно держит `frps.service` и управляющий `hermes-rdp.service`;
- Telegram показывает один Multi-PC dashboard;
- «Windows-PC-01» доступен по `SERVER_IP_OR_DOMAIN:53389`;
- каждый следующий ПК получает следующий свободный порт;
- все Windows-компьютеры используют одинаковый клиент.

## 1. Подготовить данные

Нужны:

- публичный IP или DNS Hermes;
- Telegram bot token от BotFather;
- числовой Telegram user ID владельца;
- SSH-доступ к Hermes с `sudo`;
- Windows 10/11 Pro, Enterprise или Education.

## 2. Скачать стабильный серверный установщик

На Hermes:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.4/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
```

Перед запуском можно посмотреть файл:

```bash
less /tmp/install-hermes-rdp.sh
```

Считать token без записи значения в shell history:

```bash
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
```

## 3. Установить или мигрировать Hermes

### Новая установка

```bash
sudo env HERMES_RDP_REF=v1.0.4 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID
```

### Текущий сервер Hermes

```bash
sudo env HERMES_RDP_REF=v1.0.4 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID --migrate
```

Установщик создаст backup, установит FRP, API, Telegram bot, systemd units и правила UFW.

Очистить временные данные:

```bash
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

Проверить сервер:

```bash
sudo hermes-rdpctl doctor
```

Ожидается:

```text
config: OK (...)
database: OK (...)
api: OK (1.0.0)
frp-control: LISTEN 7000
api: LISTEN 7443
```

## 4. Создать код для «Домашнего ПК»

На Hermes:

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
```

Сохрани `PAIR_CODE` и `FINGERPRINT`. Код одноразовый и по умолчанию действует 900 секунд.

## 5. Установить единый Windows-клиент

На Windows открой **PowerShell от имени администратора**:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.4/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER_IP_OR_DOMAIN' -PairCode 'PAIR_CODE' -Fingerprint 'FINGERPRINT' -Name 'Windows-PC-01' -RepositoryRef 'v1.0.4'
```

Установщик:

1. проверит редакцию и разрядность Windows;
2. зарегистрирует ПК через одноразовый код;
3. скачает FRP `0.70.1` и проверит SHA-256;
4. скачает `HermesRdpAgent.ps1` из тега `v1.0.4`;
5. включит RDP и штатное firewall-правило;
6. создаст Scheduled Task `Hermes RDP Agent` от `SYSTEM`;
7. запустит FRPC и телеметрию;
8. покажет постоянный адрес.

Проверка:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 30
```

## 6. Открыть Telegram

Отправь боту:

```text
/start
```

Должен появиться один dashboard с устройством `Windows-PC-01 · :53389`.

## 7. Добавить следующий ПК

Нажми `➕ ДОБАВИТЬ ПК`. Бот выдаст новый код и готовую команду. Выполни её на нужном Windows-компьютере от администратора.

Порт будет выделен автоматически:

```text
Windows-PC-01 → :53389
Ноутбук     → :53390
Офисный ПК  → :53391
```

## 8. Проверить RDP

На любом компьютере с RDP-клиентом:

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

Для второго ПК используй его порт из Telegram.

## Что читать дальше

- [Полная установка сервера](INSTALL_SERVER.md)
- [Полная установка Windows](INSTALL_WINDOWS.md)
- [Миграция старой схемы](MIGRATION.md)
- [Диагностика](TROUBLESHOOTING.md)
