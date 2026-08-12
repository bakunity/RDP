$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$BaseDir = 'C:\ProgramData\HermesRDP'
$ConfigPath = Join-Path $BaseDir 'device.json'
$StatePath = Join-Path $BaseDir 'agent-state.json'
$LogPath = Join-Path $BaseDir 'agent.log'
$SshErrorLog = Join-Path $BaseDir 'ssh-error.log'
$PollSeconds = 3
$SlowTelemetrySeconds = 15
$TopProcessesSeconds = 6
$SshDiscoverySeconds = 15
$script:Http = $null
$script:LiveTelemetry = $false
$script:SlowTelemetry = $null
$script:SlowTelemetryCapturedAt = 0
$script:TopProcesses = @()
$script:TopProcessesCapturedAt = 0
$script:HermesSshPids = @()
$script:SshDiscoveryCapturedAt = 0

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
    param([switch]$ForceRefresh)

    $Now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $CacheAge = $Now - [int64]$script:SshDiscoveryCapturedAt

    if (-not $ForceRefresh -and $CacheAge -lt $SshDiscoverySeconds) {
        $Cached = @()
        $CacheValid = $true
        foreach ($PidValue in @($script:HermesSshPids)) {
            try {
                $Process = Get-Process -Id ([int]$PidValue) -ErrorAction Stop
                if ($Process.ProcessName -ne 'ssh') {
                    $CacheValid = $false
                    break
                }
                $Cached += [pscustomobject]@{
                    ProcessId = [int]$Process.Id
                }
            }
            catch {
                $CacheValid = $false
                break
            }
        }
        if ($CacheValid) {
            return @($Cached)
        }
    }

    # Full WMI discovery is intentionally outside the normal 3-second path.
    # It runs at startup, periodically, or immediately after cached PID loss.
    $KeyPath = [string]$Config.ssh_key_path
    $Matches = @(
        Get-CimInstance `
            Win32_Process `
            -Filter "Name='ssh.exe'" `
            -ErrorAction SilentlyContinue |
            Where-Object {
                $_.CommandLine -and $_.CommandLine.Contains($KeyPath)
            }
    )

    $script:HermesSshPids = @(
        $Matches | ForEach-Object { [int]$_.ProcessId }
    )
    $script:SshDiscoveryCapturedAt = $Now
    return @($Matches)
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
    $script:HermesSshPids = @([int]$Process.Id)
    $script:SshDiscoveryCapturedAt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    return "SSH-туннель запущен, PID $($Process.Id)"
}

function Stop-SshTunnel {
    $Processes = @(Get-SshProcesses -ForceRefresh)
    foreach ($Process in $Processes) {
        Stop-Process -Id $Process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    $script:HermesSshPids = @()
    $script:SshDiscoveryCapturedAt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
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
    param([object[]]$Sessions = @())
    try {
        $User = (Get-CimInstance Win32_ComputerSystem).UserName
        if ($User) {
            return ($User -split '\\')[-1]
        }
    }
    catch {
    }
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

function ConvertFrom-NetstatEndpoint {
    param([string]$Endpoint)

    if ([string]::IsNullOrWhiteSpace($Endpoint)) {
        return $null
    }
    if ($Endpoint -match '^\[(.+)\]:(\d+)$') {
        return [pscustomobject]@{
            address = [string]$Matches[1]
            port = [int]$Matches[2]
        }
    }
    if ($Endpoint -match '^(.+):(\d+)$') {
        return [pscustomobject]@{
            address = [string]$Matches[1]
            port = [int]$Matches[2]
        }
    }
    return $null
}

function Get-LoopbackPeerPid {
    param(
        [int]$ClientPort,
        [int]$ServerPort = 3389
    )

    $LoopbackAddresses = @('127.0.0.1', '::1')
    try {
        $NetstatPath = Join-Path $env:WINDIR 'System32\netstat.exe'
        foreach ($Line in @(& $NetstatPath -ano -p tcp 2>$null)) {
            $Fields = @($Line.Trim() -split '\s+')
            if ($Fields.Count -lt 5 -or $Fields[0] -ne 'TCP') {
                continue
            }
            $Local = ConvertFrom-NetstatEndpoint -Endpoint $Fields[1]
            $Remote = ConvertFrom-NetstatEndpoint -Endpoint $Fields[2]
            if (-not $Local -or -not $Remote) {
                continue
            }
            if (
                $Local.port -eq $ClientPort -and
                $Remote.port -eq $ServerPort -and
                $LoopbackAddresses -contains $Local.address -and
                $LoopbackAddresses -contains $Remote.address
            ) {
                return [int]$Fields[-1]
            }
        }
    }
    catch {
    }
    return 0
}

function Get-RdpConnectionSummary {
    param([object[]]$SshProcesses = @())

    # Use the in-process .NET TCP table for the normal fast path. This avoids
    # the expensive NetTCPIP/CIM provider behind Get-NetTCPConnection.
    $LoopbackAddresses = @('127.0.0.1', '::1')
    $RdpConnections = @()
    try {
        $RdpConnections = @(
            [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpConnections() |
                Where-Object {
                    $_.State -eq [System.Net.NetworkInformation.TcpState]::Established -and
                    $_.LocalEndPoint.Port -eq 3389
                }
        )
    }
    catch {
        $RdpConnections = @()
    }

    $HermesSshPids = @(
        $SshProcesses |
            ForEach-Object { [int]($_.ProcessId) }
    )

    $HermesCount = 0
    $DirectCount = 0
    $OtherLocalCount = 0
    $RemoteAddresses = @()
    $DirectRemoteAddresses = @()

    foreach ($Connection in $RdpConnections) {
        $RemoteAddress = [string]$Connection.RemoteEndPoint.Address
        $RemotePort = [int]$Connection.RemoteEndPoint.Port
        if ($RemoteAddress -and $RemoteAddresses -notcontains $RemoteAddress) {
            $RemoteAddresses += $RemoteAddress
        }

        if ($LoopbackAddresses -notcontains $RemoteAddress) {
            $DirectCount += 1
            if (
                $RemoteAddress -and
                $DirectRemoteAddresses -notcontains $RemoteAddress
            ) {
                $DirectRemoteAddresses += $RemoteAddress
            }
            continue
        }

        # PID lookup is needed only for an actual loopback RDP session. A
        # native netstat snapshot is used instead of a second NetTCPIP query.
        $PeerPid = Get-LoopbackPeerPid -ClientPort $RemotePort -ServerPort 3389
        if ($PeerPid -gt 0 -and $HermesSshPids -contains $PeerPid) {
            $HermesCount += 1
        }
        else {
            $OtherLocalCount += 1
        }
    }

    return [pscustomobject]@{
        total = [int]$RdpConnections.Count
        hermes = [int]$HermesCount
        direct = [int]$DirectCount
        other_local = [int]$OtherLocalCount
        remote_addresses = @($RemoteAddresses)
        direct_remote_addresses = @($DirectRemoteAddresses)
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

function Get-SlowTelemetry {
    $Os = Get-CimInstance Win32_OperatingSystem
    $Disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $RamTotal = [int64]$Os.TotalVisibleMemorySize * 1KB
    $RamFree = [int64]$Os.FreePhysicalMemory * 1KB
    $RamUsed = [math]::Max(0, [int64]($RamTotal - $RamFree))
    $DiskTotal = [int64]$Disk.Size
    $DiskFree = [int64]$Disk.FreeSpace
    $DiskUsed = [math]::Max(0, [int64]($DiskTotal - $DiskFree))
    $Network = Get-NetworkTotals
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

    return [ordered]@{
        resource_captured_at = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        computer_name = $env:COMPUTERNAME
        os = $Os.Caption
        interactive_user = Get-InteractiveUser -Sessions $Sessions
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
        uptime_seconds = $Uptime
    }
}

function Get-Telemetry {
    param(
        [object]$State,
        [object[]]$SshProcesses = @(),
        [bool]$LiveTelemetry = $false
    )

    $Now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $SlowInterval = if ($LiveTelemetry) { $PollSeconds } else { $SlowTelemetrySeconds }
    if (
        -not $script:SlowTelemetry -or
        ($Now - [int64]$script:SlowTelemetryCapturedAt) -ge $SlowInterval
    ) {
        $script:SlowTelemetry = Get-SlowTelemetry
        $script:SlowTelemetryCapturedAt = [int64]$script:SlowTelemetry.resource_captured_at
    }

    if (
        $LiveTelemetry -and
        (
            $script:TopProcessesCapturedAt -eq 0 -or
            ($Now - [int64]$script:TopProcessesCapturedAt) -ge $TopProcessesSeconds
        )
    ) {
        $script:TopProcesses = @(Get-TopProcesses)
        $script:TopProcessesCapturedAt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    }

    $Rdp = Get-RdpConnectionSummary -SshProcesses $SshProcesses
    $TunnelRunning = $SshProcesses.Count -gt 0
    $Slow = $script:SlowTelemetry

    return [ordered]@{
        captured_at = $Now
        telemetry_profile = if ($LiveTelemetry) { 'live' } else { 'background' }
        resource_captured_at = [int64]$Slow.resource_captured_at
        computer_name = $Slow.computer_name
        os = $Slow.os
        interactive_user = $Slow.interactive_user
        sessions = @($Slow.sessions)
        cpu_percent = $Slow.cpu_percent
        ram_total_bytes = [int64]$Slow.ram_total_bytes
        ram_used_bytes = [int64]$Slow.ram_used_bytes
        ram_percent = $Slow.ram_percent
        disk_total_bytes = [int64]$Slow.disk_total_bytes
        disk_used_bytes = [int64]$Slow.disk_used_bytes
        disk_percent = $Slow.disk_percent
        network_received_bytes = [int64]$Slow.network_received_bytes
        network_sent_bytes = [int64]$Slow.network_sent_bytes
        route = $Slow.route
        access_enabled = [bool]$State.enabled
        ssh_tunnel_running = $TunnelRunning
        ssh_process_count = [int]$SshProcesses.Count
        rdp_connections = [int]$Rdp.total
        rdp_hermes_connections = [int]$Rdp.hermes
        rdp_direct_connections = [int]$Rdp.direct
        rdp_other_local_connections = [int]$Rdp.other_local
        rdp_remote_addresses = @($Rdp.remote_addresses)
        rdp_direct_remote_addresses = @($Rdp.direct_remote_addresses)
        uptime_seconds = [int]$Slow.uptime_seconds
        top_processes = if ($LiveTelemetry) { @($script:TopProcesses) } else { @() }
        top_processes_captured_at = if ($LiveTelemetry) {
            [int64]$script:TopProcessesCapturedAt
        }
        else { 0 }
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
                }
                'off' {
                    $State.enabled = $false
                }
                'restart' {
                    $State.enabled = $true
                }
                default {
                    throw "Неизвестная команда: $($Command.action)"
                }
            }

            # Persist control-plane state before touching transport. A failed
            # SSH action must never leave the agent believing the opposite of
            # the server's durable desired state.
            $State.last_command_seq = [int]$Command.seq
            Write-JsonFile -Path $StatePath -Value $State

            switch ([string]$Command.action) {
                'on' {
                    $Message = Start-SshTunnel
                }
                'off' {
                    $Message = Stop-SshTunnel
                }
                'restart' {
                    $Message = Restart-SshTunnel
                }
            }
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

try {
    [void](Get-SshProcesses -ForceRefresh)
}
catch {
    Write-AgentLog "Initial SSH discovery failed: $($_.Exception.Message)"
}

Write-AgentLog 'Hermes RDP OpenSSH Agent started'

while ($true) {
    $Cycle = [Diagnostics.Stopwatch]::StartNew()

    # Control/heartbeat always runs before transport reconciliation. This is
    # deliberate: if SSH is rejected or broken, the agent must still be able
    # to learn a new desired state and receive OFF/ON/RESTART commands.
    try {
        $State = Get-AgentState
        $SshProcesses = @(Get-SshProcesses)
        $Telemetry = Get-Telemetry `
            -State $State `
            -SshProcesses $SshProcesses `
            -LiveTelemetry $script:LiveTelemetry

        $Response = Invoke-ApiPost `
            -Url "$($Config.api_base_url)/v1/devices/$($Config.device_id)/telemetry" `
            -Token $Config.device_token `
            -Body @{ telemetry = $Telemetry }

        if (
            $Response -and
            $Response.PSObject.Properties['telemetry_live']
        ) {
            $script:LiveTelemetry = [bool]$Response.telemetry_live
        }

        if (
            $Response -and
            $Response.PSObject.Properties['desired_enabled']
        ) {
            $DesiredEnabled = [bool]$Response.desired_enabled
            if ([bool]$State.enabled -ne $DesiredEnabled) {
                $State.enabled = $DesiredEnabled
                Write-JsonFile -Path $StatePath -Value $State
            }
        }

        if ($Response -and $Response.command) {
            Invoke-CommandAction -Command $Response.command
        }
    }
    catch {
        Write-AgentLog "Control poll error: $($_.Exception.Message)"
    }

    # Transport recovery is intentionally isolated from the control poll.
    # Failure here is logged and retried next cycle without suppressing the
    # next heartbeat/control request.
    try {
        $State = Get-AgentState
        $SshProcesses = @(Get-SshProcesses)

        if ($State.enabled -and $SshProcesses.Count -eq 0) {
            [void](Start-SshTunnel)
        }
        elseif (-not $State.enabled -and $SshProcesses.Count -gt 0) {
            [void](Stop-SshTunnel)
        }
    }
    catch {
        Write-AgentLog "Transport reconcile error: $($_.Exception.Message)"
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
