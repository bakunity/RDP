# Команды

## Сервер

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
sudo hermes-rdpctl devices rename DEVICE_ID 'Новое имя'
sudo hermes-rdpctl devices delete DEVICE_ID
sudo hermes-rdpctl dashboard reset
```

## Windows

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Start-ScheduledTask -TaskName 'Hermes RDP Agent'
Stop-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```
