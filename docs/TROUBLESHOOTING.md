# Диагностика Hermes RDP

Начинай с раздела по симптому. Не переустанавливай всю систему, пока не собраны логи сервера и конкретного Windows-клиента.

## Базовая проверка

На Hermes:

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo systemctl is-active frps.service hermes-rdp.service
```

```bash
sudo hermes-rdpctl devices list
```

На Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
```

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
```

## Telegram bot не отвечает на `/start`

Проверить controller:

```bash
sudo systemctl --no-pager --full status hermes-rdp.service
```

```bash
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

Проверить DNS и Telegram API:

```bash
getent ahosts api.telegram.org | head
```

Проверить token без вывода значения:

```bash
sudo test -s /etc/hermes-rdp/telegram-token && echo TOKEN_FILE=OK || echo TOKEN_FILE=MISSING
```

Убедись, что тот же bot token не используется другим polling/webhook-процессом.

## Dashboard удалён, `/start` ничего не создаёт или редактируется старое сообщение

```bash
sudo hermes-rdpctl dashboard reset
```

```bash
sudo systemctl restart hermes-rdp.service
```

Затем отправь `/start`.

## Устройство показывает OFFLINE

ONLINE определяется по `last_seen`. По умолчанию OFFLINE наступает после 15 секунд без telemetry.

На Windows:

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
```

```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine.Contains('HermesRdpAgent.ps1') } | Select-Object ProcessId,CreationDate,CommandLine
```

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
```

Проверить API port:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 7443
```

На сервере:

```bash
sudo journalctl -u hermes-rdp.service --since '-15 minutes' --no-pager
```

Частые причины:

- Scheduled Task остановлена;
- Karing/VPN изменил маршрут или блокирует API;
- server fingerprint/config устарел;
- device был revoked;
- PowerShell agent падает на сборе telemetry;
- системное время сильно неверно.

## В dashboard `Пользователь: нет`

Агент сначала читает `Win32_ComputerSystem.UserName`, затем использует первую активную `quser` session. Если обе проверки пустые, UI показывает `нет`.

Проверить:

```powershell
(Get-CimInstance Win32_ComputerSystem).UserName
```

```powershell
quser.exe
```

Для RDP-сессии строка `Сессии:` важнее поля interactive user. В текущем agent fallback уже использует active session.

## FRPC не запускается

Проверить process:

```powershell
Get-Process frpc -ErrorAction SilentlyContinue
```

Проверить config:

```powershell
& 'C:\ProgramData\HermesRDP\frpc.exe' verify -c 'C:\ProgramData\HermesRDP\frpc.toml'
```

Ручной тест:

```powershell
& 'C:\ProgramData\HermesRDP\frpc.exe' -c 'C:\ProgramData\HermesRDP\frpc.toml'
```

Не оставляй ручной FRPC запущенным одновременно с Scheduled Task.

## FRPC не подключается к Hermes

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 7000
```

На Hermes:

```bash
sudo systemctl status frps.service --no-pager
```

```bash
sudo journalctl -u frps.service -n 100 --no-pager
```

```bash
sudo ss -lntp | grep ':7000\b'
```

Проверить:

- адрес и port в `frpc.toml`;
- TLS CA file существует;
- FRP token совпадает;
- proxy remote port входит в `allowPorts`;
- другой client не использует тот же proxy name/port;
- firewall пропускает `7000/tcp`.

## `bad permissions` для приватного ключа

Hermes RDP v1.0.0 не использует SSH private key для telemetry: агент отправляет HTTPS с device token. Такая ошибка относится к старому Windows Monitor и означает, что legacy task ещё запущена.

Проверить старые задачи:

```powershell
Get-ScheduledTask | Where-Object TaskName -in @('Hermes Windows Monitor','Hermes FRPC Client','Hermes RDP Telegram Bot')
```

После успешной установки v1 должна остаться задача:

```text
Hermes RDP Agent
```

## RDP endpoint закрыт

Узнать порт:

```bash
sudo hermes-rdpctl devices list
```

Проверить с внешнего компьютера:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

На Windows target:

```powershell
Get-Service TermService
```

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

```powershell
Get-NetFirewallRule -Name 'RemoteDesktop-*' | Select-Object DisplayName,Enabled,Direction,Action
```

На Hermes:

```bash
sudo ss -lntp | grep ':53389\b'
```

```bash
sudo ufw status numbered
```

Интерпретация:

- FRPC stopped → нажать ON или проверить agent;
- FRPC running, но server port не слушает → проверить FRPS logs/proxy;
- server port слушает, RDP не открывается → проверить TermService/firewall/credentials;
- endpoint доступен, login не проходит → проблема Windows account/NLA/password, не FRP.

## ON/OFF/RESTART не применяется

На Telegram экран может показать отправленную команду до её получения Windows.

Проверить, что устройство ONLINE. Затем:

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
```

На сервере:

```bash
sudo journalctl -u hermes-rdp.service --since '-10 minutes' --no-pager
```

Команда доставляется только во время telemetry POST. OFF не выключает agent, только FRPC.

## Pair code expired или already used

Создать новый:

```bash
sudo hermes-rdpctl pair create --name 'Название ПК'
```

Pair code нельзя использовать второй раз даже на том же компьютере.

## Порт уже занят

```text
port 53389 is already assigned
```

Посмотреть устройства:

```bash
sudo hermes-rdpctl devices list
```

Для нового ПК не указывай `--port`, тогда сервер выберет следующий свободный.

Если старое устройство больше не нужно:

```bash
sudo hermes-rdpctl devices delete DEVICE_ID
```

Останови старый Windows agent до повторного использования порта.

## Нет свободных RDP-портов

По умолчанию доступно 32 порта. Проверить диапазон:

```bash
sudo cat /etc/hermes-rdp/config.json
```

```bash
sudo grep -A3 allowPorts /etc/frp/frps.toml
```

Расширение диапазона описано в [OPERATIONS.md](OPERATIONS.md).

## API fingerprint mismatch

Не отключай проверку fingerprint.

Серверный fingerprint:

```bash
sudo cat /etc/hermes-rdp/tls/api.sha256
```

Создай новый pair command и используй fingerprint именно с текущего доверенного сервера. Если сертификат API был заменён, старые клиенты продолжат отклонять сервер до обновления `device.json`/переустановки.

## После обновления server не запускается

```bash
sudo systemctl --no-pager --full status hermes-rdp.service
```

```bash
sudo journalctl -u hermes-rdp.service -n 150 --no-pager
```

```bash
sudo python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp
```

Проверить config:

```bash
sudo python3 -m json.tool /etc/hermes-rdp/config.json >/dev/null && echo CONFIG_JSON=OK
```

Updater пишет backup path. Восстанови код из соответствующего `/var/backups/hermes-rdp/update-*` и перезапусти сервис.

## Какие данные присылать разработчику

Безопасный диагностический набор:

Hermes:

```bash
sudo hermes-rdpctl doctor
sudo systemctl --no-pager --full status frps.service hermes-rdp.service
sudo journalctl -u frps.service -n 80 --no-pager
sudo journalctl -u hermes-rdp.service -n 120 --no-pager
sudo hermes-rdpctl devices list
```

Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent' | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
Get-Process frpc -ErrorAction SilentlyContinue | Select-Object Id,StartTime,Path
```

Не отправляй:

- `/etc/hermes-rdp/telegram-token`;
- `/etc/hermes-rdp/frp-token`;
- `device.json`;
- `frpc.toml`;
- TLS private keys;
- полный server backup.
