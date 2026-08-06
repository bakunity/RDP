# Команды

## Сервер

```bash
sudo hermes-rdpctl status
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Ноутбук'
sudo hermes-rdpctl pair create --name 'Домашний ПК' --port 53389
sudo hermes-rdpctl device rename DEVICE_ID 'Новое имя'
sudo hermes-rdpctl device revoke DEVICE_ID
sudo journalctl -u hermes-rdp -f
sudo journalctl -u frps -f
```

## Windows

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

## Обновление

Сервер:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/update-server.sh | sudo bash
```

Windows, PowerShell от администратора:

```powershell
irm https://raw.githubusercontent.com/bakunity/RDP/main/scripts/update-client.ps1 | iex
```
