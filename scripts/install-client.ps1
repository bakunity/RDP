param(
    [Parameter(Mandatory = $true)]
    [string]$Server,

    [Parameter(Mandatory = $true)]
    [string]$PairCode,

    [Parameter(Mandatory = $true)]
    [string]$Fingerprint,

    [string]$Name,
    [int]$ApiPort = 7443,
    [string]$RepositoryRef = 'main'
)

#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http
$ProgressPreference = 'SilentlyContinue'

$Repo = 'bakunity/RDP'
$FrpVersion = '0.70.1'
$FrpSha256 = '531f3cd3cc41c0b4f077b54fe6b7dd83c0ff727e7f0bf412a4c78fa279165de5'
$BaseDir = 'C:\ProgramData\HermesRDP'
$TaskName = 'Hermes RDP Agent'
$ApiBase = "https://${Server}:${ApiPort}"
$script:ExpectedFingerprint = ($Fingerprint -replace '[^0-9A-Fa-f]', '').ToUpperInvariant()
$CurrentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$CurrentPrincipal = New-Object Security.Principal.WindowsPrincipal($CurrentIdentity)
if (-not $CurrentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Открой PowerShell от имени администратора.'
}

function New-PinnedHttpClient {
    $Handler = New-Object System.Net.Http.HttpClientHandler
    $Handler.ServerCertificateCustomValidationCallback = {
        param($Request, $Certificate, $Chain, $SslPolicyErrors)
        try {
            $Sha = [Security.Cryptography.SHA256]::Create()
            try {
                $Actual = ([BitConverter]::ToString(
                    $Sha.ComputeHash($Certificate.GetRawCertData())
                )).Replace('-', '').ToUpperInvariant()
            }
            finally {
                $Sha.Dispose()
            }
            return $Actual -eq $script:ExpectedFingerprint
        }
        catch { return $false }
    }
    $Client = New-Object System.Net.Http.HttpClient($Handler)
    $Client.Timeout = [TimeSpan]::FromSeconds(30)
    return $Client
}

function Invoke-PinnedPost {
    param([System.Net.Http.HttpClient]$Client, [string]$Url, [object]$Body)
    $Json = $Body | ConvertTo-Json -Depth 8 -Compress
    $Content = New-Object System.Net.Http.StringContent(
        $Json,
        [Text.Encoding]::UTF8,
        'application/json'
    )
    $Response = $Client.PostAsync($Url, $Content).GetAwaiter().GetResult()
    $Text = $Response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    if (-not $Response.IsSuccessStatusCode) {
        throw "HTTP $([int]$Response.StatusCode): $Text"
    }
    return $Text | ConvertFrom-Json
}

function Set-SecretAcl {
    param([string]$Path)
    $Acl = Get-Acl -LiteralPath $Path
    $Acl.SetSecurityDescriptorSddlForm('O:SYG:SYD:P(A;;FA;;;SY)(A;;FA;;;BA)')
    Set-Acl -LiteralPath $Path -AclObject $Acl
}

Write-Host '=== HERMES RDP WINDOWS INSTALLER ===' -ForegroundColor Cyan

$LegacyTasks = @(
    'Hermes FRPC Client',
    'Hermes Windows Monitor',
    'Hermes RDP Telegram Bot',
    $TaskName
)
foreach ($LegacyTask in $LegacyTasks) {
    Stop-ScheduledTask -TaskName $LegacyTask -ErrorAction SilentlyContinue
    if ($LegacyTask -ne $TaskName) {
        Unregister-ScheduledTask -TaskName $LegacyTask -Confirm:$false -ErrorAction SilentlyContinue
    }
}
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        ($_.Name -eq 'frpc.exe') -or
        ($_.CommandLine -and (
            $_.CommandLine.Contains('windows-monitor.ps1') -or
            $_.CommandLine.Contains('HermesRdpAgent.ps1')
        ))
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
if ([Environment]::Is64BitOperatingSystem -ne $true) {
    throw 'Поддерживается только 64-битная Windows.'
}
if (-not $Name) {
    $Name = Read-Host 'Название компьютера в Telegram'
}
if ([string]::IsNullOrWhiteSpace($Name)) {
    $Name = $env:COMPUTERNAME
}

$Os = Get-CimInstance Win32_OperatingSystem
if ($Os.ProductType -ne 1) {
    throw 'Установщик предназначен для клиентской Windows.'
}
$RdpEditionSupported = $Os.Caption -match 'Pro|Enterprise|Education|Server'
if (-not $RdpEditionSupported) {
    throw "Редакция '$($Os.Caption)' не поддерживает входящие RDP-подключения."
}

$BackupDir = Join-Path $BaseDir ('backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (Test-Path -LiteralPath $BaseDir) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Get-ChildItem -LiteralPath $BaseDir -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne 'backups' } |
        Copy-Item -Destination $BackupDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $BaseDir -Force | Out-Null

$MachineFingerprint = (Get-CimInstance Win32_ComputerSystemProduct).UUID
$Http = New-PinnedHttpClient
try {
    $Health = $Http.GetStringAsync("$ApiBase/healthz").GetAwaiter().GetResult() | ConvertFrom-Json
    if (($Health.fingerprint -replace '[^0-9A-Fa-f]', '').ToUpperInvariant() -ne $script:ExpectedFingerprint) {
        throw 'Fingerprint в ответе сервера не совпал.'
    }
    $Pair = Invoke-PinnedPost -Client $Http -Url "$ApiBase/v1/pair" -Body @{
        code = $PairCode.ToUpperInvariant()
        display_name = $Name
        machine_name = $env:COMPUTERNAME
        fingerprint = $MachineFingerprint
    }
}
finally {
    $Http.Dispose()
}

$Temp = Join-Path $env:TEMP ('hermes-rdp-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $Temp -Force | Out-Null
try {
    $Zip = Join-Path $Temp 'frp.zip'
    $FrpUrl = "https://github.com/fatedier/frp/releases/download/v$FrpVersion/frp_${FrpVersion}_windows_amd64.zip"
    Invoke-WebRequest -UseBasicParsing -Uri $FrpUrl -OutFile $Zip
    $ActualSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $Zip).Hash.ToLowerInvariant()
    if ($ActualSha -ne $FrpSha256) {
        throw "FRP SHA-256 mismatch: $ActualSha"
    }
    Expand-Archive -LiteralPath $Zip -DestinationPath $Temp -Force
    $FrpcSource = Get-ChildItem -LiteralPath $Temp -Filter frpc.exe -Recurse | Select-Object -First 1
    if (-not $FrpcSource) { throw 'frpc.exe не найден в архиве.' }
    Copy-Item -LiteralPath $FrpcSource.FullName -Destination (Join-Path $BaseDir 'frpc.exe') -Force

    $AgentUrl = "https://raw.githubusercontent.com/$Repo/$RepositoryRef/client/HermesRdpAgent.ps1"
    Invoke-WebRequest -UseBasicParsing -Uri $AgentUrl -OutFile (Join-Path $BaseDir 'HermesRdpAgent.ps1')
}
finally {
    Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
}

$CaPath = Join-Path $BaseDir 'frp-ca.crt'
[IO.File]::WriteAllText($CaPath, [string]$Pair.frp.ca_pem, [Text.UTF8Encoding]::new($false))
$Config = [ordered]@{
    device_id = [string]$Pair.device.id
    device_name = [string]$Pair.device.name
    device_token = [string]$Pair.device.token
    server = $Server
    api_base_url = $ApiBase
    api_fingerprint = $script:ExpectedFingerprint
    rdp_port = [int]$Pair.device.rdp_port
}
$ConfigPath = Join-Path $BaseDir 'device.json'
$Config | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ConfigPath -Encoding UTF8

$FrpcToml = @"
serverAddr = "$($Pair.frp.server_addr)"
serverPort = $([int]$Pair.frp.server_port)
auth.method = "token"
auth.token = "$($Pair.frp.token)"
transport.tls.enable = true
transport.tls.serverName = "$($Pair.frp.server_addr)"
transport.tls.trustedCaFile = "$($CaPath.Replace('\', '\\'))"

[[proxies]]
name = "rdp-$($Pair.device.id)"
type = "tcp"
localIP = "127.0.0.1"
localPort = 3389
remotePort = $([int]$Pair.device.rdp_port)
"@
$FrpcConfigPath = Join-Path $BaseDir 'frpc.toml'
[IO.File]::WriteAllText($FrpcConfigPath, $FrpcToml, [Text.UTF8Encoding]::new($false))

# Enable RDP and firewall rule without changing the user's authentication policy.
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Get-NetFirewallRule -Name 'RemoteDesktop-*' -ErrorAction SilentlyContinue | Enable-NetFirewallRule
Set-Service -Name TermService -StartupType Automatic
Start-Service -Name TermService

$Action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BaseDir\HermesRdpAgent.ps1`""
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Trigger.Delay = 'PT20S'
$Principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Settings $Settings `
    -Force | Out-Null

foreach ($Secret in @($ConfigPath, $FrpcConfigPath)) {
    Set-SecretAcl -Path $Secret
}
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 8

Write-Host
Write-Host '=== ГОТОВО ===' -ForegroundColor Green
Write-Host "Компьютер: $($Pair.device.name)"
Write-Host "RDP: ${Server}:$($Pair.device.rdp_port)"
Write-Host "Устройство: $($Pair.device.id)"
Write-Host "Задача: $TaskName"
Write-Host "Лог: $BaseDir\agent.log"
