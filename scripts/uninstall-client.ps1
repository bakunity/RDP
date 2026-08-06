#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
$BaseDir = 'C:\ProgramData\HermesRDP'
$TaskName = 'Hermes RDP Agent'
$Answer = Read-Host 'Введите REMOVE для удаления клиента'
if ($Answer -ne 'REMOVE') { exit 1 }
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        ($_.ExecutablePath -eq "$BaseDir\frpc.exe") -or
        ($_.CommandLine -and $_.CommandLine.Contains("$BaseDir\HermesRdpAgent.ps1"))
    } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
$Backup = "$BaseDir.removed.$(Get-Date -Format yyyyMMdd-HHmmss)"
Move-Item -LiteralPath $BaseDir -Destination $Backup -Force
Write-Host "Клиент удалён. Архив: $Backup"
Write-Host 'В Telegram удали устройство, чтобы отозвать его API-токен и освободить порт.'
