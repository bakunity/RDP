# Диагностика

## Бот не отвечает после удаления dashboard

```bash
sudo hermes-rdpctl dashboard reset
sudo systemctl restart hermes-rdp.service
```

Затем отправь `/start`.

## Windows показывает OFFLINE

На Windows:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDPgent.log' -Tail 100
```

На сервере:

```bash
sudo hermes-rdpctl doctor
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

## FRPC не подключается

```powershell
& 'C:\ProgramData\HermesRDPrpc.exe' verify -c 'C:\ProgramData\HermesRDPrpc.toml'
Test-NetConnection SERVER -Port 7000
```

## RDP endpoint закрыт

Проверь:

- агент ONLINE;
- FRPC показывает `работает`;
- Windows service `TermService` запущен;
- локальный порт 3389 слушается;
- публичный RDP-порт разрешён firewall сервера.

## Проверка серверных портов

```bash
sudo ss -lntp | grep -E ':(7000|7443|53389)\b'
sudo ufw status numbered
```
