param([string]$RepositoryRef = 'main')
#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
$BaseDir = 'C:\ProgramData\HermesRDP'
$TaskName = 'Hermes RDP Agent'
$AgentPath = Join-Path $BaseDir 'HermesRdpAgent.ps1'
if (-not (Test-Path -LiteralPath $AgentPath)) { throw 'Hermes RDP Agent не установлен.' }
$Backup = "$AgentPath.$(Get-Date -Format yyyyMMdd-HHmmss).bak"
Copy-Item -LiteralPath $AgentPath -Destination $Backup -Force
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($AgentPath) } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
$Url = "https://raw.githubusercontent.com/bakunity/RDP/$RepositoryRef/client/HermesRdpAgent.ps1"
Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $AgentPath
$Tokens = $null
$Errors = $null
[void][Management.Automation.Language.Parser]::ParseFile($AgentPath, [ref]$Tokens, [ref]$Errors)
if ($Errors.Count -gt 0) {
    Copy-Item -LiteralPath $Backup -Destination $AgentPath -Force
    throw $Errors[0].Message
}
Start-ScheduledTask -TaskName $TaskName
Write-Host "Обновлено. Backup: $Backup"
