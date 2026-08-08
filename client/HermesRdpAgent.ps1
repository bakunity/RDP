$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$BaseDir = 'C:\ProgramData\HermesRDP'
$ConfigPath = Join-Path $BaseDir 'device.json'
$StatePath = Join-Path $BaseDir 'agent-state.json'
$LogPath = Join-Path $BaseDir 'agent.log'
$SshErrorLog = Join-Path $BaseDir 'ssh-error.log'
$PollSeconds = 3
$script:Http = $null

$PinnedHttpClientSource = @'
using System;
using System.Net.Http;
using System.Net.Security;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;

namespace HermesRdp
{
    public static class AgentPinnedHttpClientFactory
    {
        private static string Normalize(string value)
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

        public static HttpClient Create(string fingerprint)
        {
            string expected = Normalize(fingerprint);
            var handler = new HttpClientHandler();
            handler.ServerCertificateCustomValidationCallback = delegate(
                HttpRequestMessage request,
                X509Certificate2 certificate,
                X509Chain chain,
                SslPolicyErrors errors)
            {
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
            };
            var client = new HttpClient(handler);
            client.Timeout = TimeSpan.FromSeconds(20);
            return client;
        }
    }
}
'@

if (-not ('HermesRdp.AgentPinnedHttpClientFactory' -as [type])) {
    Add-Type `
        -TypeDefinition $PinnedHttpClientSource `
        -Language CSharp `
        -ReferencedAssemblies 'System.Net.Http.dll'
}

function Write-AgentLog {
    param([string]$Message)
    $Line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
    try {
        $Info = Get-Item -LiteralPath $LogPath -ErrorAction Stop
        if ($Info.Length -gt 2MB) {
            Get-Content -LiteralPath $LogPath -Tail 1000 |
                Set-Content -LiteralPath "$LogPath.tmp" -Encoding UTF8
            Move-Item -LiteralPath "$LogPath.tmp" -Destination $LogPath -Force
        }
    }
    catch {
    }
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Write-JsonFile {
    param([string]$Path, [object]$Value)
    $Temp = "$Path.tmp"
    $Value | ConvertTo-Json -Depth 10 |
        Set-Content -LiteralPath $Temp -Encoding UTF8
    Move-Item -LiteralPath $Temp -Destination $Path -Force
}

function Get-AgentState {
    $State = Read-JsonFile -Path $StatePath
    if (-not $State) {
        $State = [pscustomobject]@{
            enabled = $true
            last_command_seq = 0
        }
        Write-JsonFile -Path $StatePath -Value $State
    }
    return $State
}

function Invoke-ApiPost {
    param(
        [string]$Url,
        [object]$Body,
        [string]$Token
    )
    $Json = $Body | ConvertTo-Json -Depth 12 -Compress
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
        $Response = $script:Http.SendAsync($Request).GetAwaiter().GetResult()
        try {
            $Content = $Response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $Response.IsSuccessStatusCode) {
                throw "HTTP $([int]$Response.StatusCode): $Content"
            }
            if ([string]::IsNullOrWhiteSpace($Content)) {
                return $null
            }
            return $Content | ConvertFrom-Json
        }
        finally {
            $Response.Dispose()
        }
    }
    finally {
        $Request.Dispose()
    }
}

function Get-SshProcesses {
    # The private key path is unique per Hermes device and is more reliable
    # than matching the exact rendered -R command line on every Windows build.
    $KeyPath = [string]$Config.ssh_key_path
    return @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -eq 'ssh.exe' -and
                $_.CommandLine -and
                $_.CommandLine.Contains($KeyPath)
            }
    )
}

function Start-SshTunnel {
    if ((Get-SshProcesses).Count -gt 0) {
        return 'SSH-туннель уже запущен'
    }

    if (-not (Test-Path -LiteralPath $Config.ssh_path)) {
        throw "Не найден ssh.exe: $($Config.ssh_path)"
    }

    $Arguments = @(
        '-N'
        '-T'
        '-p'
        [string]$Config.ssh_port
        '-i'
        [string]$Config.ssh_key_path
        '-o'
        'BatchMode=yes'
        '-o'
        'ExitOnForwardFailure=yes'
        '-o'
        'ServerAliveInterval=30'
        '-o'
        'ServerAliveCountMax=3'
        '-o'
        'ConnectTimeout=15'
        '-o'
        'StrictHostKeyChecking=yes'
        '-o'
        "UserKnownHostsFile=$($Config.known_hosts_path)"
        '-o'
        'GlobalKnownHostsFile=NUL'
        '-o'
        'LogLevel=ERROR'
        '-R'
        "0.0.0.0:$($Config.rdp_port):127.0.0.1:3389"
        "$($Config.ssh_user)@$($Config.server)"
    )

    if (Test-Path -LiteralPath $SshErrorLog) {
        Remove-Item -LiteralPath $SshErrorLog -Force -ErrorAction SilentlyContinue
    }

    $Process = Start-Process `
        -FilePath $Config.ssh_path `
        -ArgumentList $Arguments `
        -WorkingDirectory $BaseDir `
        -WindowStyle Hidden `
        -RedirectStandardError $SshErrorLog `
        -PassThru

    Start-Sleep -Seconds 3
    if ($Process.HasExited) {
        $Detail = ''
        if (Test-Path -LiteralPath $SshErrorLog) {
            $Detail = (
                Get-Content -LiteralPath $SshErrorLog -Tail 20 |
                    Out-String
            ).Trim()
        }
        throw "SSH завершился с кодом $($Process.ExitCode): $Detail"
    }
    return "SSH-туннель запущен, PID $($Process.Id)"
}

function Stop-SshTunnel {
    $Processes = @(Get-SshProcesses)
    foreach ($Process in $Processes) {
        Stop-Process -Id $Process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    return "SSH-туннель остановлен ($($Processes.Count) процессов)"
}

function Restart-SshTunnel {
    [void](Stop-SshTunnel)
    Start-Sleep -Seconds 1
    return Start-SshTunnel
}

function Get-CpuPercent {
    try {
        $Value = Get-CimInstance `
            Win32_PerfFormattedData_PerfOS_Processor `
            -Filter "Name='_Total'" `
            -ErrorAction Stop
        return [math]::Round([double]$Value.PercentProcessorTime, 1)
    }
    catch {
        return 0.0
    }
}

function Get-Sessions {
    $Names = @()
    try {
        $Lines = quser.exe 2>$null
        foreach ($Line in @($Lines | Select-Object -Skip 1)) {
            $Clean = ($Line -replace '^>', '').Trim()
            if ($Clean) {
                $Name = ($Clean -split '\s+')[0]
                if ($Name -and $Names -notcontains $Name) {
                    $Names += $Name
                }
            }
        }
    }
    catch {
    }
    return $Names
}

function Get-InteractiveUser {
    try {
        $User = (Get-CimInstance Win32_ComputerSystem).UserName
        if ($User) {
            return ($User -split '\\')[-1]
        }
    }
    catch {
    }
    $Sessions = @(Get-Sessions)
    if ($Sessions.Count -gt 0) {
        return $Sessions[0]
    }
    return $null
}

function Get-NetworkTotals {
    $Received = [int64]0
    $Sent = [int64]0
    try {
        foreach ($Adapter in Get-NetAdapterStatistics -ErrorAction Stop) {
            $Received += [int64]$Adapter.ReceivedBytes
            $Sent += [int64]$Adapter.SentBytes
        }
    }
    catch {
    }
    return @($Received, $Sent)
}

function Test-TcpPort {
    param(
        [string]$HostName,
        [int]$Port,
        [int]$TimeoutMs = 1500
    )
    $Client = New-Object Net.Sockets.TcpClient
    try {
        $Async = $Client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $Async.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) {
            return $false
        }
        $Client.EndConnect($Async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $Client.Close()
    }
}

function Get-RouteName {
    try {
        $Route = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction Stop |
            Sort-Object RouteMetric, InterfaceMetric |
            Select-Object -First 1
        if ($Route) {
            $Adapter = Get-NetAdapter `
                -InterfaceIndex $Route.InterfaceIndex `
                -ErrorAction SilentlyContinue
            if ($Adapter) {
                return $Adapter.Name
            }
        }
    }
    catch {
    }
    return '—'
}

function Get-TopProcesses {
    $First = @{}
    foreach ($Process in Get-Process -ErrorAction SilentlyContinue) {
        try {
            $First[$Process.Id] = [double]$Process.CPU
        }
        catch {
        }
    }
    Start-Sleep -Milliseconds 800
    $Elapsed = 0.8
    $Logical = [Environment]::ProcessorCount
    $Rows = @()
    foreach ($Process in Get-Process -ErrorAction SilentlyContinue) {
        try {
            $Before = if ($First.ContainsKey($Process.Id)) {
                $First[$Process.Id]
            }
            else {
                [double]$Process.CPU
            }
            $Delta = [math]::Max(
                0.0,
                [double]$Process.CPU - $Before
            )
            $Percent = [math]::Round(
                ($Delta / $Elapsed / $Logical) * 100,
                1
            )
            $Rows += [pscustomobject]@{
                name = $Process.ProcessName
                pid = $Process.Id
                cpu_percent = $Percent
                memory_bytes = [int64]$Process.WorkingSet64
            }
        }
        catch {
        }
    }
    return @(
        $Rows |
            Sort-Object cpu_percent, memory_bytes -Descending |
            Select-Object -First 5
    )
}

function Get-Telemetry {
    $Os = Get-CimInstance Win32_OperatingSystem
    $Disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $RamTotal = [int64]$Os.TotalVisibleMemorySize * 1KB
    $RamFree = [int64]$Os.FreePhysicalMemory * 1KB
    $RamUsed = [math]::Max(0, [int64]($RamTotal - $RamFree))
    $DiskTotal = [int64]$Disk.Size
    $DiskFree = [int64]$Disk.FreeSpace
    $DiskUsed = [math]::Max(0, [int64]($DiskTotal - $DiskFree))
    $Network = Get-NetworkTotals
    $RdpConnections = @(
        Get-NetTCPConnection `
            -LocalPort 3389 `
            -State Established `
            -ErrorAction SilentlyContinue
    )
    $RemoteAddresses = @(
        $RdpConnections |
            Select-Object -ExpandProperty RemoteAddress -Unique |
            Where-Object { $_ }
    )
    $Sessions = @(Get-Sessions)
    $Boot = if ($Os.LastBootUpTime -is [datetime]) {
        [datetime]$Os.LastBootUpTime
    }
    else {
        [Management.ManagementDateTimeConverter]::ToDateTime(
            [string]$Os.LastBootUpTime
        )
    }
    $Uptime = [int]((Get-Date) - $Boot).TotalSeconds
    $State = Get-AgentState
    $SshProcesses = @(Get-SshProcesses)
    $TunnelRunning = $SshProcesses.Count -gt 0
    $EndpointAvailable = Test-TcpPort `
        -HostName $Config.server `
        -Port ([int]$Config.rdp_port) `
        -TimeoutMs 1500

    return [ordered]@{
        captured_at = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        computer_name = $env:COMPUTERNAME
        os = $Os.Caption
        interactive_user = Get-InteractiveUser
        sessions = $Sessions
        cpu_percent = Get-CpuPercent
        ram_total_bytes = $RamTotal
        ram_used_bytes = $RamUsed
        ram_percent = if ($RamTotal -gt 0) {
            [math]::Round(($RamUsed / $RamTotal) * 100, 1)
        }
        else { 0 }
        disk_total_bytes = $DiskTotal
        disk_used_bytes = $DiskUsed
        disk_percent = if ($DiskTotal -gt 0) {
            [math]::Round(($DiskUsed / $DiskTotal) * 100, 1)
        }
        else { 0 }
        network_received_bytes = [int64]$Network[0]
        network_sent_bytes = [int64]$Network[1]
        route = Get-RouteName
        access_enabled = [bool]$State.enabled
        ssh_tunnel_running = $TunnelRunning
        ssh_process_count = [int]$SshProcesses.Count
        endpoint_available = [bool]$EndpointAvailable
        rdp_connections = $RdpConnections.Count
        rdp_remote_addresses = $RemoteAddresses
        uptime_seconds = $Uptime
        top_processes = @(Get-TopProcesses)
    }
}

function Invoke-CommandAction {
    param([object]$Command)
    $State = Get-AgentState
    $Ok = $true
    $Message = ''
    try {
        if ([int]$Command.seq -le [int]$State.last_command_seq) {
            $Message = 'Команда уже применена'
        }
        else {
            switch ([string]$Command.action) {
                'on' {
                    $State.enabled = $true
                    $Message = Start-SshTunnel
                }
                'off' {
                    $State.enabled = $false
                    $Message = Stop-SshTunnel
                }
                'restart' {
                    $State.enabled = $true
                    $Message = Restart-SshTunnel
                }
                default {
                    throw "Неизвестная команда: $($Command.action)"
                }
            }
            $State.last_command_seq = [int]$Command.seq
            Write-JsonFile -Path $StatePath -Value $State
        }
    }
    catch {
        $Ok = $false
        $Message = $_.Exception.Message
    }
    try {
        [void](Invoke-ApiPost `
            -Url "$($Config.api_base_url)/v1/devices/$($Config.device_id)/command-result" `
            -Token $Config.device_token `
            -Body @{
                seq = [int]$Command.seq
                ok = $Ok
                message = $Message
            })
    }
    catch {
        Write-AgentLog "Command result upload failed: $($_.Exception.Message)"
    }
}

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    throw "Не найден конфиг: $ConfigPath"
}

$Config = Read-JsonFile -Path $ConfigPath
$script:Http = [HermesRdp.AgentPinnedHttpClientFactory]::Create(
    [string]$Config.api_fingerprint
)
$State = Get-AgentState

if ($State.enabled) {
    try {
        [void](Start-SshTunnel)
    }
    catch {
        Write-AgentLog $_.Exception.Message
    }
}
else {
    [void](Stop-SshTunnel)
}

Write-AgentLog 'Hermes RDP OpenSSH Agent started'

while ($true) {
    $Cycle = [Diagnostics.Stopwatch]::StartNew()
    try {
        $State = Get-AgentState
        if ($State.enabled -and (Get-SshProcesses).Count -eq 0) {
            [void](Start-SshTunnel)
        }
        if (-not $State.enabled -and (Get-SshProcesses).Count -gt 0) {
            [void](Stop-SshTunnel)
        }

        $Telemetry = Get-Telemetry
        $Response = Invoke-ApiPost `
            -Url "$($Config.api_base_url)/v1/devices/$($Config.device_id)/telemetry" `
            -Token $Config.device_token `
            -Body @{ telemetry = $Telemetry }

        if ($Response.command) {
            Invoke-CommandAction -Command $Response.command
        }
    }
    catch {
        Write-AgentLog "Loop error: $($_.Exception.Message)"
    }
    finally {
        $Cycle.Stop()
    }

    $SleepMs = [math]::Max(
        250,
        [int](($PollSeconds * 1000) - $Cycle.ElapsedMilliseconds)
    )
    Start-Sleep -Milliseconds $SleepMs
}
