# Эксплуатация Hermes RDP

Практический runbook для сервера и Windows-клиентов.

## Ежедневная проверка Hermes

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo systemctl --no-pager --full status frps.service hermes-rdp.service
```

```bash
sudo hermes-rdpctl devices list
```

Нормальное состояние:

- `frps.service` — active;
- `hermes-rdp.service` — active;
- API и FRP control слушают порты;
- ONLINE-устройства имеют небольшой `last_seen`;
- RDP endpoint выбранного включённого ПК доступен.

## Логи

Controller/API/Telegram:

```bash
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

LIVE:

```bash
sudo journalctl -u hermes-rdp.service -f
```

FRPS:

```bash
sudo journalctl -u frps.service -n 100 --no-pager
```

Windows:

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
```

## Управление устройствами

Список:

```bash
sudo hermes-rdpctl devices list
```

Новый code с автоматическим портом:

```bash
sudo hermes-rdpctl pair create --name 'Ноутбук'
```

Новый code с конкретным портом:

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
```

Переименование:

```bash
sudo hermes-rdpctl devices rename DEVICE_ID 'Новое имя'
```

Отзыв:

```bash
sudo hermes-rdpctl devices delete DEVICE_ID
```

Отзыв помечает device как revoked и блокирует API token. После этого запусти локальный uninstall на Windows.

## Telegram dashboard

После ручного удаления сообщения:

```bash
sudo hermes-rdpctl dashboard reset
```

```bash
sudo systemctl restart hermes-rdp.service
```

Затем отправь `/start`.

## Restart services

Controller без остановки FRP tunnels:

```bash
sudo systemctl restart hermes-rdp.service
```

FRPS — временно разорвёт все tunnels:

```bash
sudo systemctl restart frps.service
```

FRPC-клиенты должны переподключиться автоматически.

## Backup server

Основные данные:

```text
/etc/hermes-rdp/
/etc/frp/
/var/lib/hermes-rdp/state.sqlite3
/opt/hermes-rdp/
/etc/systemd/system/hermes-rdp.service
/etc/systemd/system/frps.service
```

Создать ручной архив:

```bash
sudo tar -C / -czf "/root/hermes-rdp-backup-$(date -u +%Y%m%dT%H%M%SZ).tar.gz" etc/hermes-rdp etc/frp var/lib/hermes-rdp opt/hermes-rdp etc/systemd/system/hermes-rdp.service etc/systemd/system/frps.service
```

Проверить архив:

```bash
sudo tar -tzf /root/hermes-rdp-backup-*.tar.gz | head
```

SQLite использует WAL. Для консистентного online backup предпочтительно:

```bash
sudo python3 - <<'PY'
import sqlite3
src = sqlite3.connect('/var/lib/hermes-rdp/state.sqlite3')
dst = sqlite3.connect('/root/hermes-rdp-state-backup.sqlite3')
with dst:
    src.backup(dst)
dst.close()
src.close()
print('/root/hermes-rdp-state-backup.sqlite3')
PY
```

## Restore server

1. остановить сервисы;
2. сохранить текущие повреждённые файлы отдельно;
3. восстановить config, secrets, TLS и SQLite;
4. проверить владельцев и permissions;
5. выполнить daemon-reload;
6. запустить FRPS, затем controller;
7. выполнить `doctor`.

```bash
sudo systemctl stop hermes-rdp.service frps.service
```

После восстановления:

```bash
sudo systemctl daemon-reload
sudo systemctl start frps.service hermes-rdp.service
sudo hermes-rdpctl doctor
```

Не публикуй backup: он содержит Telegram token, FRP token, TLS keys и device data.

## Update server

Стабильная версия:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.5/scripts/update-server.sh -o /tmp/update-hermes-rdp.sh
```

```bash
sudo env HERMES_RDP_REF=v1.0.5 bash /tmp/update-hermes-rdp.sh
```

```bash
rm -f /tmp/update-hermes-rdp.sh
```

Updater сохраняет `/opt/hermes-rdp`, config и systemd unit в `/var/backups/hermes-rdp/update-<timestamp>`.

После update:

```bash
sudo hermes-rdpctl doctor
```

## Update Windows client

PowerShell от администратора:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.5/scripts/update-client.ps1'; & ([scriptblock]::Create((irm $u))) -RepositoryRef 'v1.0.5'
```

Проверка:

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 30
```

## Rotate Telegram token

```bash
read -rsp 'New Telegram token: ' TG_TOKEN; echo
```

```bash
printf '%s\n' "$TG_TOKEN" | sudo tee /etc/hermes-rdp/telegram-token >/dev/null
sudo chown root:hermes-rdp /etc/hermes-rdp/telegram-token
sudo chmod 0640 /etc/hermes-rdp/telegram-token
sudo systemctl restart hermes-rdp.service
unset TG_TOKEN
```

## Rotate FRP token

Ротация общего FRP token разрывает все клиенты. Процедура требует подготовленного окна:

1. создать новый token;
2. изменить server config;
3. обновить `frpc.toml` каждого доверенного Windows ПК;
4. перезапустить FRPS;
5. перезапустить agents;
6. проверить endpoints.

Подробности: [SECURITY.md](SECURITY.md).

## Освобождение порта

`devices delete` помечает device revoked. `allocate_port` игнорирует revoked devices, поэтому порт становится доступен для нового pairing. Перед повторной выдачей убедись, что старый FRPC больше не запущен, иначе он может пытаться подключаться со старым общим FRP token.

## Capacity

Диапазон `53389–53420` содержит 32 порта, то есть максимум 32 активных non-revoked устройства. Для увеличения:

1. расширить `allowPorts` в `/etc/frp/frps.toml`;
2. изменить `port_end` в `/etc/hermes-rdp/config.json`;
3. открыть диапазон UFW;
4. перезапустить службы;
5. проверить, что новый диапазон не конфликтует с другими сервисами.

## Удаление server

Перед uninstall обязательно сделать backup. Скрипт удаления останавливает сервисы и удаляет project files, но правила firewall и внешние backups следует проверить вручную.
