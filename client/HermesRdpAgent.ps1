$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$BaseDir = 'C:\ProgramData\HermesRDP'
$ConfigPath = Join-Path $BaseDir 'device.json'
$StatePath = Join-Path $BaseDir 'agent-state.json'
$LogPath = Join-Path $BaseDir 'agent.log'
$FrpcPath = Join-Path $BaseDir 'frpc.exe'
$FrpcConfig = Join-Path $BaseDir 'frpc.toml'
$PollSeconds = 3
$script:ExpectedFingerprint = ''
$script:Http = $null

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

function New-PinnedHttpClient {
    param([string]$Fingerprint)
    $script:ExpectedFingerprint = ($Fingerprint -replace '[^0-9A-Fa-f]', '').ToUpperInvariant()
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
        catch {
            return $false
        }
    }
    $Client = New-Object System.Net.Http.HttpClient($Handler)
    $Client.Timeout = [TimeSpan]::FromSeconds(20)
    return $Client
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
        $Request.Headers.Authorization = New-Object System.Net.Http.Headers.AuthenticationHeaderValue(
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

function Get-FrpcProcesses {
    return Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ExecutablePath -eq $FrpcPath -or
            ($_.Name -eq 'frpc.exe' -and $_.CommandLine -like "*$FrpcConfig*")
        }
}

function Start-Frpc {
    $Existing = @(Get-FrpcProcesses)
    if ($Existing.Count -gt 0) {
        return 'FRPC уже запущен'
    }
    $Process = Start-Process -FilePath $FrpcPath `
        -ArgumentList @('-c', $FrpcConfig) `
        -WorkingDirectory $BaseDir `
        -WindowStyle Hidden `
        -PassThru
    Start-Sleep -Seconds 2
    if ($Process.HasExited) {
        throw "FRPC завершился с кодом $($Process.ExitCode)"
    }
    return "FRPC запущен, PID $($Process.Id)"
}

function Stop-Frpc {
    $Processes = @(Get-FrpcProcesses)
    foreach ($Process in $Processes) {
        Stop-Process -Id $Process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    return "FRPC остановлен ($($Processes.Count) процессов)"
}

function Restart-Frpc {
    [void](Stop-Frpc)
    Start-Sleep -Seconds 1
    return Start-Frpc
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
            $Adapter = Get-NetAdapter -InterfaceIndex $Route.InterfaceIndex -ErrorAction SilentlyContinue
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
            $Before = if ($First.ContainsKey($Process.Id)) { $First[$Process.Id] } else { [double]$Process.CPU }
            $Delta = [math]::Max(0.0, [double]$Process.CPU - $Before)
            $Percent = [math]::Round(($Delta / $Elapsed / $Logical) * 100, 1)
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
    return @($Rows | Sort-Object cpu_percent, memory_bytes -Descending | Select-Object -First 5)
}

function Get-Telemetry {
    $Os = Get-CimInstance Win32_OperatingSystem
    $Disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $RamTotal = [int64]$Os.TotalVisibleMemorySize * 1KB
    $RamFree = [int64]$Os.FreePhysicalMemory * 1KB
    $RamUsed = [int64]($RamTotal - $RamFree)
    if ($RamUsed -lt 0) { $RamUsed = 0 }
    $DiskTotal = [int64]$Disk.Size
    $DiskFree = [int64]$Disk.FreeSpace
    $DiskUsed = [int64]($DiskTotal - $DiskFree)
    if ($DiskUsed -lt 0) { $DiskUsed = 0 }
    $Network = Get-NetworkTotals
    $RdpConnections = @(
        Get-NetTCPConnection -LocalPort 3389 -State Established -ErrorAction SilentlyContinue
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
    $FrpcRunning = @(Get-FrpcProcesses).Count -gt 0
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
        ram_percent = if ($RamTotal -gt 0) { [math]::Round(($RamUsed / $RamTotal) * 100, 1) } else { 0 }
        disk_total_bytes = $DiskTotal
        disk_used_bytes = $DiskUsed
        disk_percent = if ($DiskTotal -gt 0) { [math]::Round(($DiskUsed / $DiskTotal) * 100, 1) } else { 0 }
        network_received_bytes = [int64]$Network[0]
        network_sent_bytes = [int64]$Network[1]
        route = Get-RouteName
        frpc_running = $FrpcRunning
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
                $Message = Start-Frpc
            }
            'off' {
                $State.enabled = $false
                $Message = Stop-Frpc
            }
            'restart' {
                $State.enabled = $true
                $Message = Restart-Frpc
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
$script:Http = New-PinnedHttpClient -Fingerprint $Config.api_fingerprint
$State = Get-AgentState
if ($State.enabled) {
    try { [void](Start-Frpc) } catch { Write-AgentLog $_.Exception.Message }
}
else {
    [void](Stop-Frpc)
}
Write-AgentLog 'Hermes RDP Agent started'

while ($true) {
    $Cycle = [Diagnostics.Stopwatch]::StartNew()
    try {
        $State = Get-AgentState
        if ($State.enabled -and @(Get-FrpcProcesses).Count -eq 0) {
            [void](Start-Frpc)
        }
        if (-not $State.enabled -and @(Get-FrpcProcesses).Count -gt 0) {
            [void](Stop-Frpc)
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
    $SleepMs = [math]::Max(250, [int](($PollSeconds * 1000) - $Cycle.ElapsedMilliseconds))
    Start-Sleep -Milliseconds $SleepMs
}
