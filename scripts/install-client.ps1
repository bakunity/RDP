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
$ProgressPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Net.Http

$Repo = 'bakunity/RDP'
$BaseDir = 'C:\ProgramData\HermesRDP'
$TaskName = 'Hermes RDP Agent'
$ApiBase = "https://${Server}:${ApiPort}"
$ExpectedFingerprint = (
    $Fingerprint -replace '[^0-9A-Fa-f]', ''
).ToUpperInvariant()

$CurrentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$CurrentPrincipal = New-Object Security.Principal.WindowsPrincipal(
    $CurrentIdentity
)
if (-not $CurrentPrincipal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)) {
    throw 'Открой PowerShell от имени администратора.'
}

$PinnedHttpClientSource = @'
using System;
using System.Net.Http;
using System.Net.Security;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;

namespace HermesRdp
{
    public static class PinnedHttpClientFactory
    {
        private static string NormalizeFingerprint(string value)
        {
            var result = new StringBuilder();
            if (value == null) return String.Empty;
            foreach (char character in value)
            {
                if (Uri.IsHexDigit(character))
                    result.Append(Char.ToUpperInvariant(character));
            }
            return result.ToString();
        }

        public static bool ValidateCertificate(
            X509Certificate2 certificate,
            string expectedFingerprint)
        {
            string expected = NormalizeFingerprint(expectedFingerprint);
            if (certificate == null || expected.Length != 64) return false;
            using (SHA256 sha = SHA256.Create())
            {
                string actual = BitConverter.ToString(
                    sha.ComputeHash(certificate.RawData)
                ).Replace("-", String.Empty);
                return String.Equals(
                    actual,
                    expected,
                    StringComparison.OrdinalIgnoreCase
                );
            }
        }

        public static HttpClient Create(string expectedFingerprint)
        {
            string expected = NormalizeFingerprint(expectedFingerprint);
            var handler = new HttpClientHandler();
            handler.ServerCertificateCustomValidationCallback = delegate(
                HttpRequestMessage request,
                X509Certificate2 certificate,
                X509Chain chain,
                SslPolicyErrors errors)
            {
                return ValidateCertificate(certificate, expected);
            };
            var client = new HttpClient(handler);
            client.Timeout = TimeSpan.FromSeconds(30);
            return client;
        }
    }
}
'@

if (-not ('HermesRdp.PinnedHttpClientFactory' -as [type])) {
    Add-Type `
        -TypeDefinition $PinnedHttpClientSource `
        -Language CSharp `
        -ReferencedAssemblies 'System.Net.Http.dll'
}

function Invoke-PinnedPost {
    param(
        [System.Net.Http.HttpClient]$Client,
        [string]$Url,
        [object]$Body,
        [string]$Token
    )
    $Json = $Body | ConvertTo-Json -Depth 8 -Compress
    $Request = New-Object System.Net.Http.HttpRequestMessage(
        [System.Net.Http.HttpMethod]::Post,
        $Url
    )
    $Request.Content = New-Object System.Net.Http.StringContent(
        $Json,
        [Text.Encoding]::UTF8,
        'application/json'
    )
    if ($Token) {
        $Request.Headers.Authorization =
            New-Object System.Net.Http.Headers.AuthenticationHeaderValue(
                'Bearer',
                $Token
            )
    }
    try {
        $Response = $Client.SendAsync($Request).GetAwaiter().GetResult()
        try {
            $Text = $Response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $Response.IsSuccessStatusCode) {
                throw "HTTP $([int]$Response.StatusCode): $Text"
            }
            if ([string]::IsNullOrWhiteSpace($Text)) {
                return $null
            }
            return $Text | ConvertFrom-Json
        }
        finally {
            $Response.Dispose()
        }
    }
    finally {
        $Request.Dispose()
    }
}

function Set-SecretAcl {
    param([string]$Path)
    $Acl = Get-Acl -LiteralPath $Path
    $Acl.SetSecurityDescriptorSddlForm(
        'O:SYG:SYD:P(A;;FA;;;SY)(A;;FA;;;BA)'
    )
    Set-Acl -LiteralPath $Path -AclObject $Acl
}

function Stop-HermesProcesses {
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            ($_.Name -eq 'frpc.exe') -or
            ($_.Name -eq 'ssh.exe' -and $_.CommandLine -and
                $_.CommandLine.Contains('HermesRDP')) -or
            ($_.CommandLine -and
                $_.CommandLine.Contains('HermesRdpAgent.ps1'))
        } |
        ForEach-Object {
            Stop-Process `
                -Id $_.ProcessId `
                -Force `
                -ErrorAction SilentlyContinue
        }
}

function Ensure-OpenSshClient {
    $SshPath = Join-Path $env:WINDIR 'System32\OpenSSH\ssh.exe'
    $KeygenPath = Join-Path $env:WINDIR 'System32\OpenSSH\ssh-keygen.exe'
    if (
        (Test-Path -LiteralPath $SshPath) -and
        (Test-Path -LiteralPath $KeygenPath)
    ) {
        return @{
            ssh = $SshPath
            keygen = $KeygenPath
        }
    }

    $Capability = Get-WindowsCapability `
        -Online `
        -Name 'OpenSSH.Client*' |
        Select-Object -First 1

    if (-not $Capability) {
        throw 'Компонент OpenSSH Client не найден в Windows.'
    }
    if ($Capability.State -ne 'Installed') {
        Write-Host 'Устанавливаю стандартный OpenSSH Client Windows...'
        Add-WindowsCapability `
            -Online `
            -Name $Capability.Name |
            Out-Null
    }

    if (
        -not (Test-Path -LiteralPath $SshPath) -or
        -not (Test-Path -LiteralPath $KeygenPath)
    ) {
        throw 'OpenSSH Client не появился после установки компонента Windows.'
    }

    return @{
        ssh = $SshPath
        keygen = $KeygenPath
    }
}

Write-Host '=== HERMES RDP OPENSSH INSTALLER ===' -ForegroundColor Cyan

if ([Environment]::Is64BitOperatingSystem -ne $true) {
    throw 'Поддерживается только 64-битная Windows.'
}

$Os = Get-CimInstance Win32_OperatingSystem
if ($Os.ProductType -ne 1) {
    throw 'Установщик предназначен для клиентской Windows.'
}
if ($Os.Caption -notmatch 'Pro|Enterprise|Education|Server') {
    throw "Редакция '$($Os.Caption)' не поддерживает входящие RDP-подключения."
}

if (-not $Name) {
    $Name = Read-Host 'Название компьютера в Telegram'
}
if ([string]::IsNullOrWhiteSpace($Name)) {
    $Name = $env:COMPUTERNAME
}

$OpenSsh = Ensure-OpenSshClient
$SshPath = [string]$OpenSsh.ssh
$KeygenPath = [string]$OpenSsh.keygen

$LegacyTasks = @(
    'Hermes FRPC Client'
    'Hermes Windows Monitor'
    'Hermes RDP Telegram Bot'
    $TaskName
)
foreach ($LegacyTask in $LegacyTasks) {
    Stop-ScheduledTask `
        -TaskName $LegacyTask `
        -ErrorAction SilentlyContinue
    if ($LegacyTask -ne $TaskName) {
        Unregister-ScheduledTask `
            -TaskName $LegacyTask `
            -Confirm:$false `
            -ErrorAction SilentlyContinue
    }
}
Stop-HermesProcesses

$BackupDir = Join-Path $BaseDir (
    'backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss')
)
if (Test-Path -LiteralPath $BaseDir) {
    New-Item `
        -ItemType Directory `
        -Path $BackupDir `
        -Force |
        Out-Null
    Get-ChildItem `
        -LiteralPath $BaseDir `
        -Force `
        -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne 'backups' } |
        Copy-Item `
            -Destination $BackupDir `
            -Recurse `
            -Force `
            -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $BaseDir -Force | Out-Null

$AgentPath = Join-Path $BaseDir 'HermesRdpAgent.ps1'
$AgentUrl = (
    "https://raw.githubusercontent.com/$Repo/" +
    "$RepositoryRef/client/HermesRdpAgent.ps1"
)
Invoke-WebRequest `
    -UseBasicParsing `
    -Uri $AgentUrl `
    -OutFile $AgentPath

$Tokens = $null
$ParseErrors = $null
[void][Management.Automation.Language.Parser]::ParseFile(
    $AgentPath,
    [ref]$Tokens,
    [ref]$ParseErrors
)
if ($ParseErrors.Count -gt 0) {
    throw "Agent parse error: $($ParseErrors[0].Message)"
}

$SshKeyPath = Join-Path $BaseDir 'id_ed25519'
$SshPublicKeyPath = "$SshKeyPath.pub"
if (
    -not (Test-Path -LiteralPath $SshKeyPath) -or
    -not (Test-Path -LiteralPath $SshPublicKeyPath)
) {
    Remove-Item `
        -LiteralPath $SshKeyPath, $SshPublicKeyPath `
        -Force `
        -ErrorAction SilentlyContinue
    & $KeygenPath `
        -q `
        -t ed25519 `
        -N '' `
        -C "hermes-rdp-$env:COMPUTERNAME" `
        -f $SshKeyPath
    if ($LASTEXITCODE -ne 0) {
        throw "ssh-keygen завершился с кодом $LASTEXITCODE"
    }
}

$PublicKeyParts = (
    Get-Content -LiteralPath $SshPublicKeyPath -Raw
).Trim().Split(
    [char[]]" `t",
    [StringSplitOptions]::RemoveEmptyEntries
)
if ($PublicKeyParts.Count -lt 2 -or $PublicKeyParts[0] -ne 'ssh-ed25519') {
    throw 'Сгенерирован некорректный SSH Ed25519 public key.'
}
$PublicKey = "$($PublicKeyParts[0]) $($PublicKeyParts[1])"
$MachineFingerprint = (Get-CimInstance Win32_ComputerSystemProduct).UUID

$Http = [HermesRdp.PinnedHttpClientFactory]::Create(
    $ExpectedFingerprint
)
$Pair = $null
try {
    $Health = $Http.GetStringAsync(
        "$ApiBase/healthz"
    ).GetAwaiter().GetResult() | ConvertFrom-Json

    if (
        (
            $Health.fingerprint -replace '[^0-9A-Fa-f]', ''
        ).ToUpperInvariant() -ne $ExpectedFingerprint
    ) {
        throw 'Fingerprint в ответе сервера не совпал.'
    }
    if ([string]$Health.tunnel -ne 'openssh') {
        throw 'Сервер ещё не переведён на Hermes RDP OpenSSH.'
    }

    $Pair = Invoke-PinnedPost `
        -Client $Http `
        -Url "$ApiBase/v1/pair" `
        -Body @{
            code = $PairCode.ToUpperInvariant()
            display_name = $Name
            machine_name = $env:COMPUTERNAME
            fingerprint = $MachineFingerprint
            ssh_public_key = $PublicKey
        }

    $KnownHostsPath = Join-Path $BaseDir 'known_hosts'
    $KnownHostLine = (
        "[$Server]:$($Pair.ssh.port) " +
        [string]$Pair.ssh.host_key
    )
    [IO.File]::WriteAllText(
        $KnownHostsPath,
        "$KnownHostLine`n",
        [Text.UTF8Encoding]::new($false)
    )

    $Config = [ordered]@{
        device_id = [string]$Pair.device.id
        device_name = [string]$Pair.device.name
        device_token = [string]$Pair.device.token
        server = $Server
        api_base_url = $ApiBase
        api_fingerprint = $ExpectedFingerprint
        rdp_port = [int]$Pair.device.rdp_port
        ssh_path = $SshPath
        ssh_port = [int]$Pair.ssh.port
        ssh_user = [string]$Pair.ssh.user
        ssh_key_path = $SshKeyPath
        known_hosts_path = $KnownHostsPath
    }

    $ConfigPath = Join-Path $BaseDir 'device.json'
    $Config |
        ConvertTo-Json -Depth 5 |
        Set-Content -LiteralPath $ConfigPath -Encoding UTF8

    Set-ItemProperty `
        -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' `
        -Name fDenyTSConnections `
        -Value 0
    Get-NetFirewallRule `
        -Name 'RemoteDesktop-*' `
        -ErrorAction SilentlyContinue |
        Enable-NetFirewallRule
    Set-Service -Name TermService -StartupType Automatic
    Start-Service -Name TermService

    $Action = New-ScheduledTaskAction `
        -Execute 'powershell.exe' `
        -Argument (
            '-NoProfile -ExecutionPolicy Bypass -File ' +
            "`"$AgentPath`""
        )
    $Trigger = New-ScheduledTaskTrigger -AtStartup
    $Trigger.Delay = 'PT20S'
    $Principal = New-ScheduledTaskPrincipal `
        -UserId 'SYSTEM' `
        -LogonType ServiceAccount `
        -RunLevel Highest
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
        -Force |
        Out-Null

    foreach ($Secret in @(
        $ConfigPath,
        $SshKeyPath,
        $KnownHostsPath
    )) {
        Set-SecretAcl -Path $Secret
    }

    Remove-Item `
        -LiteralPath (
            Join-Path $BaseDir 'frpc.exe'
        ), (
            Join-Path $BaseDir 'frpc.toml'
        ), (
            Join-Path $BaseDir 'frp-ca.crt'
        ) `
        -Force `
        -ErrorAction SilentlyContinue

    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 8

    $TunnelProcess = Get-CimInstance `
        Win32_Process `
        -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -eq 'ssh.exe' -and
            $_.CommandLine -and
            $_.CommandLine.Contains($SshKeyPath)
        } |
        Select-Object -First 1

    if (-not $TunnelProcess) {
        $Log = Join-Path $BaseDir 'agent.log'
        $Detail = if (Test-Path -LiteralPath $Log) {
            (
                Get-Content -LiteralPath $Log -Tail 20 |
                    Out-String
            ).Trim()
        }
        else {
            'agent.log ещё не создан'
        }
        throw "SSH-туннель не запустился. $Detail"
    }

    Write-Host
    Write-Host '=== ГОТОВО ===' -ForegroundColor Green
    Write-Host "Компьютер: $($Pair.device.name)"
    Write-Host "RDP: ${Server}:$($Pair.device.rdp_port)"
    Write-Host "Туннель: OpenSSH"
    Write-Host "Задача: $TaskName"
    Write-Host "Лог: $BaseDir\agent.log"
}
catch {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask `
        -TaskName $TaskName `
        -Confirm:$false `
        -ErrorAction SilentlyContinue
    Stop-HermesProcesses
    if ($Pair -and $Pair.device.id -and $Pair.device.token) {
        try {
            [void](Invoke-PinnedPost `
                -Client $Http `
                -Url (
                    "$ApiBase/v1/devices/" +
                    "$($Pair.device.id)/revoke-self"
                ) `
                -Token ([string]$Pair.device.token) `
                -Body @{ reason = 'client-install-failed' })
        }
        catch {
        }
    }
    throw
}
finally {
    $Http.Dispose()
}
