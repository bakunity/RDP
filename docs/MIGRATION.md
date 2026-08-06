# Миграция существующего Hermes RDP

Этот документ описывает перевод старой схемы `один Windows ПК + отдельный Telegram bot + FRPS ON/OFF` в Hermes RDP v1.0.4.

## Цель миграции

Сохранить:

- сервер Hermes `SERVER_IP_OR_DOMAIN`;
- endpoint домашнего ПК `SERVER_IP_OR_DOMAIN:53389`;
- существующую возможность RDP;
- Telegram bot token и доступ владельца.

Изменить:

- `frps` становится постоянно работающим сервером для всех ПК;
- ON/OFF применяется к выбранному Windows-клиенту;
- старые отдельные Windows-задачи заменяются одной задачей `Hermes RDP Agent`;
- основной ПК становится обычным устройством в общем реестре.

## Важное правило

После миграции «Windows-PC-01» не имеет специальной логики. Это просто первое зарегистрированное устройство, которому вручную закреплён порт `53389`.

## 1. Зафиксировать текущее состояние

На Hermes:

```bash
sudo systemctl status frps.service hermes-rdp-bot.service --no-pager
```

```bash
sudo ss -lntp | grep -E ':(7000|53389)\b'
```

На Windows:

```powershell
Get-ScheduledTask | Where-Object TaskName -like 'Hermes*' | Select-Object TaskName,State
```

Проверь, что текущий RDP работает до миграции.

## 2. Скачать v1.0.4

На Hermes:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.4/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
```

```bash
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
```

## 3. Запустить миграцию сервера

```bash
sudo env HERMES_RDP_REF=v1.0.4 bash /tmp/install-hermes-rdp.sh --host SERVER_IP_OR_DOMAIN --telegram-token "$TG_TOKEN" --telegram-chat-id TELEGRAM_USER_ID --migrate
```

Установщик:

- создаёт `/var/backups/hermes-rdp/<timestamp>`;
- сохраняет существующие `/etc/frp`, `/etc/hermes-rdp`, `/opt/hermes-rdp`, `/var/lib/hermes-rdp` и systemd units;
- пытается импортировать существующий FRP token;
- нормализует совместимые старые имена FRP TLS-файлов;
- отключает старый `hermes-rdp-bot.service`;
- устанавливает новый `hermes-rdp.service`;
- оставляет диапазон начиная с `53389`.

Очистить временные данные:

```bash
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

## 4. Проверить новый сервер

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo systemctl status frps.service hermes-rdp.service --no-pager
```

Не продолжай миграцию Windows, пока `doctor` не показывает `api: OK`, `frp-control: LISTEN 7000` и `api: LISTEN 7443`.

## 5. Создать запись для домашнего ПК

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
```

Сохрани `PAIR_CODE` и `FINGERPRINT`.

## 6. Установить общий клиент на текущем ПК

Открой PowerShell от администратора:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.4/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER_IP_OR_DOMAIN' -PairCode 'PAIR_CODE' -Fingerprint 'FINGERPRINT' -Name 'Windows-PC-01' -RepositoryRef 'v1.0.4'
```

Установщик сам остановит и удалит устаревшие задачи:

```text
Hermes FRPC Client
Hermes Windows Monitor
Hermes RDP Telegram Bot
```

После успешной установки останется:

```text
Hermes RDP Agent
```

## 7. Проверить результат

На Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

На Hermes:

```bash
sudo hermes-rdpctl devices list
```

В Telegram:

```text
/start
```

Ожидаемый endpoint:

```text
Windows-PC-01 → SERVER_IP_OR_DOMAIN:53389
```

Проверка подключения:

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

## 8. Добавить остальные ПК

После проверки первого ПК используй `➕ ДОБАВИТЬ ПК`. Сервер автоматически выдаст `53390`, затем `53391` и так далее.

## Откат сервера

Последний backup:

```bash
sudo readlink -f /var/backups/hermes-rdp/latest
```

Перед ручным восстановлением останови новые службы:

```bash
sudo systemctl stop hermes-rdp.service frps.service
```

Backup содержит файлы с исходными абсолютными путями. Восстановление должно выполняться осознанно по содержимому конкретного каталога, а не слепым копированием всего `/var/backups`.

## Откат Windows

Старые файлы сохраняются в:

```text
C:\ProgramData\HermesRDP\backups\<timestamp>
```

При проблеме сначала сохрани текущий `agent.log`, затем используй [диагностику](TROUBLESHOOTING.md). Не возвращай одновременно старые и новые Scheduled Tasks: два FRPC-процесса будут конфликтовать за один remote port.
