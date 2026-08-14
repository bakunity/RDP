param(
    [switch]$Once,
    [int]$IntervalSeconds = 900
)

#Requires -RunAsAdministrator
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Net.Http

$BaseDir = 'C:\ProgramData\HermesRDP'
$ConfigPath = Join-Path $BaseDir 'device.json'
$SyncPath = Join-Path $BaseDir 'sync-rdp-certificate.ps1'
$LogPath = Join-Path $BaseDir 'cert-rotation.log'
$RdpNamespace = 'root/cimv2/TerminalServices'
$RdpFilter = "TerminalName='RDP-tcp'"

if ($IntervalSeconds -lt 60) {
    $IntervalSeconds = 60
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
    public static class RotationPinnedHttpClientFactory
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
                    return String.Equals(actual, expected, StringComparison.OrdinalIgnoreCase);
                }
            };
            var client = new HttpClient(handler);
            client.Timeout = TimeSpan.FromSeconds(30);
            return client;
        }
    }
}
'@

if (-not ('HermesRdp.RotationPinnedHttpClientFactory' -as [type])) {
    Add-Type `
        -TypeDefinition $PinnedHttpClientSource `
        -Language CSharp `
        -ReferencedAssemblies 'System.Net.Http.dll'
}

function Write-RotationLog {
    param([string]$Message)

    $Line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
    try {
        $Info = Get-Item -LiteralPath $LogPath -ErrorAction Stop
        if ($Info.Length -gt 1MB) {
            Get-Content -LiteralPath $LogPath -Tail 500 |
                Set-Content -LiteralPath "$LogPath.tmp" -Encoding UTF8
            Move-Item -LiteralPath "$LogPath.tmp" -Destination $LogPath -Force
        }
    }
    catch {
    }
}

function Normalize-Thumbprint {
    param([string]$Value)
    return (($Value -replace '[^0-9A-Fa-f]', '').ToUpperInvariant())
}

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Invoke-ApiPost {
    param(
        [System.Net.Http.HttpClient]$Client,
        [string]$Url,
        [string]$Token
    )

    $Request = New-Object System.Net.Http.HttpRequestMessage(
        [System.Net.Http.HttpMethod]::Post,
        $Url
    )
    $Request.Content = New-Object System.Net.Http.StringContent(
        '{}',
        [Text.Encoding]::UTF8,
        'application/json'
    )
    $Request.Headers.Authorization =
        New-Object System.Net.Http.Headers.AuthenticationHeaderValue(
            'Bearer',
            $Token
        )

    try {
        $Response = $Client.SendAsync($Request).GetAwaiter().GetResult()
        try {
            $Text = $Response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            if (-not $Response.IsSuccessStatusCode) {
                throw "HTTP $([int]$Response.StatusCode): $Text"
            }
            if ([string]::IsNullOrWhiteSpace($Text)) {
                throw 'Hermes certificate status response is empty.'
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

function Get-RdpSetting {
    return Get-CimInstance `
        -Namespace $RdpNamespace `
        -ClassName Win32_TSGeneralSetting `
        -Filter $RdpFilter
}

function Get-NativePowerShellPath {
    $System32 = Join-Path $env:WINDIR 'System32'
    if (
        [Environment]::Is64BitOperatingSystem -and
        -not [Environment]::Is64BitProcess
    ) {
        $System32 = Join-Path $env:WINDIR 'Sysnative'
    }
    return Join-Path $System32 'WindowsPowerShell\v1.0\powershell.exe'
}

function Invoke-CertificateSync {
    if (-not (Test-Path -LiteralPath $SyncPath)) {
        throw "Hermes certificate sync script is missing: $SyncPath"
    }

    $PowerShellPath = Get-NativePowerShellPath
    if (-not (Test-Path -LiteralPath $PowerShellPath)) {
        throw "Native Windows PowerShell is missing: $PowerShellPath"
    }

    $Output = & $PowerShellPath `
        -NoProfile `
        -ExecutionPolicy Bypass `
        -File $SyncPath 2>&1 |
        Out-String
    $ExitCode = $LASTEXITCODE

    $CleanOutput = $Output.Trim()
    if ($CleanOutput) {
        foreach ($Line in @($CleanOutput -split "`r?`n")) {
            if ($Line) {
                Write-RotationLog "sync: $Line"
            }
        }
    }
    if ($ExitCode -ne 0) {
        throw "Hermes certificate sync exited with code $ExitCode"
    }
}

function Invoke-RotationCheck {
    $Config = Read-JsonFile -Path $ConfigPath
    if (-not $Config) {
        throw "Hermes device config is missing: $ConfigPath"
    }
    foreach ($Name in @('device_id', 'device_token', 'api_base_url', 'api_fingerprint')) {
        if ([string]::IsNullOrWhiteSpace([string]$Config.$Name)) {
            throw "Hermes device config is missing $Name"
        }
    }

    $Http = [HermesRdp.RotationPinnedHttpClientFactory]::Create(
        [string]$Config.api_fingerprint
    )
    try {
        $Status = Invoke-ApiPost `
            -Client $Http `
            -Url "$($Config.api_base_url)/v1/devices/$($Config.device_id)/rdp-certificate-status" `
            -Token ([string]$Config.device_token)
    }
    finally {
        $Http.Dispose()
    }

    if (-not $Status.ok) {
        throw 'Hermes certificate status response is invalid.'
    }
    if (-not [bool]$Status.enabled) {
        Write-RotationLog 'CERT_ROTATION=NOT_ENABLED'
        if ($Once) { Write-Host 'CERT_ROTATION=NOT_ENABLED' }
        return
    }
    if (-not $Status.certificate) {
        throw 'Hermes certificate status is missing certificate metadata.'
    }

    $Expected = Normalize-Thumbprint -Value ([string]$Status.certificate.thumbprint)
    if ($Expected.Length -ne 40) {
        throw 'Hermes certificate status returned invalid thumbprint.'
    }

    $Before = Get-RdpSetting
    $BeforeHash = Normalize-Thumbprint -Value ([string]$Before.SSLCertificateSHA1Hash)
    $BeforeType = [int]$Before.SSLCertificateSHA1HashType

    if ($BeforeType -eq 3 -and $BeforeHash -eq $Expected) {
        Write-RotationLog "CERT_ROTATION=UNCHANGED thumbprint=$Expected"
        if ($Once) { Write-Host 'CERT_ROTATION=UNCHANGED' }
        return
    }

    Write-RotationLog (
        "certificate drift detected: local_type=$BeforeType " +
        "local_thumbprint=$BeforeHash target_thumbprint=$Expected"
    )

    Invoke-CertificateSync

    $After = Get-RdpSetting
    $AfterHash = Normalize-Thumbprint -Value ([string]$After.SSLCertificateSHA1Hash)
    $AfterType = [int]$After.SSLCertificateSHA1HashType
    if ($AfterType -ne 3 -or $AfterHash -ne $Expected) {
        throw (
            "certificate sync verification failed: type=$AfterType " +
            "thumbprint=$AfterHash expected=$Expected"
        )
    }

    Write-RotationLog "CERT_ROTATION=UPDATED thumbprint=$AfterHash"
    if ($Once) { Write-Host 'CERT_ROTATION=UPDATED' }
}

$Mutex = New-Object System.Threading.Mutex(
    $false,
    'Global\HermesRdpCertificateRotation'
)
$HasMutex = $false
try {
    $HasMutex = $Mutex.WaitOne(0)
    if (-not $HasMutex) {
        if ($Once) { Write-Host 'CERT_ROTATION=ALREADY_RUNNING' }
        exit 0
    }

    do {
        try {
            Invoke-RotationCheck
        }
        catch {
            Write-RotationLog "CERT_ROTATION=ERROR $($_.Exception.Message)"
            if ($Once) {
                Write-Host "CERT_ROTATION=ERROR:$($_.Exception.Message)"
                exit 1
            }
        }

        if ($Once) {
            break
        }
        Start-Sleep -Seconds $IntervalSeconds
    } while ($true)
}
finally {
    if ($HasMutex) {
        try { $Mutex.ReleaseMutex() } catch {}
    }
    $Mutex.Dispose()
}
