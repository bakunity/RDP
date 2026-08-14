#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
$BaseDir = 'C:\ProgramData\HermesRDP'
$TaskName = 'Hermes RDP Agent'
$RotationTaskName = 'Hermes RDP Certificate Rotation'
$AgentPath = Join-Path $BaseDir 'HermesRdpAgent.ps1'
$RotationPath = Join-Path $BaseDir 'HermesRdpCertRotation.ps1'

$Answer = Read-Host 'Введите REMOVE для удаления клиента'
if ($Answer -ne 'REMOVE') {
    exit 1
}

foreach ($HermesTask in @($TaskName, $RotationTaskName)) {
    Stop-ScheduledTask `
        -TaskName $HermesTask `
        -ErrorAction SilentlyContinue
    Unregister-ScheduledTask `
        -TaskName $HermesTask `
        -Confirm:$false `
        -ErrorAction SilentlyContinue
}

Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        ($_.Name -eq 'frpc.exe') -or
        ($_.Name -eq 'ssh.exe' -and $_.CommandLine -and
            $_.CommandLine.Contains('HermesRDP')) -or
        ($_.CommandLine -and
            $_.CommandLine.Contains($AgentPath)) -or
        ($_.CommandLine -and
            $_.CommandLine.Contains($RotationPath))
    } |
    ForEach-Object {
        Stop-Process `
            -Id $_.ProcessId `
            -Force `
            -ErrorAction SilentlyContinue
    }

if (Test-Path -LiteralPath $BaseDir) {
    $Backup = "$BaseDir.removed.$(Get-Date -Format yyyyMMdd-HHmmss)"
    Move-Item -LiteralPath $BaseDir -Destination $Backup -Force
    Write-Host "Клиент удалён. Архив: $Backup"
}
else {
    Write-Host 'Каталог Hermes RDP уже отсутствует.'
}

Write-Host (
    'В Telegram удали устройство, чтобы отозвать API-token, ' +
    'SSH-ключ и освободить RDP-порт.'
)
