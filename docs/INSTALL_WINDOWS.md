# Установка Windows

Поддерживаются Windows 10/11 Pro, Enterprise и Education 64-bit.

1. Открой Telegram dashboard.
2. Нажми `Добавить ПК`.
3. Открой PowerShell от имени администратора.
4. Скопируй блок целиком.
5. Введи название устройства.

Установщик использует стандартные компоненты Windows OpenSSH. При их отсутствии он устанавливает capability `OpenSSH.Client` средствами Windows.

Файлы:

```text
C:\ProgramData\HermesRDP\HermesRdpAgent.ps1
C:\ProgramData\HermesRDP\device.json
C:\ProgramData\HermesRDP\id_ed25519
C:\ProgramData\HermesRDP\known_hosts
C:\ProgramData\HermesRDP\agent.log
```

Проверка:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Process ssh -ErrorAction SilentlyContinue
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```
