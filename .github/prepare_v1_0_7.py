from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[1]
old_version = "1.0.6"
new_version = "1.0.7"

installer_path = root / "scripts/install-client.ps1"
installer = installer_path.read_text(encoding="utf-8-sig")
old_function = '''function New-PinnedHttpClient {
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
'''
new_function = '''$PinnedHttpClientSource = @'
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
            if (value == null)
            {
                return String.Empty;
            }

            foreach (char character in value)
            {
                if (Uri.IsHexDigit(character))
                {
                    result.Append(Char.ToUpperInvariant(character));
                }
            }

            return result.ToString();
        }

        public static bool ValidateCertificate(
            X509Certificate2 certificate,
            string expectedFingerprint)
        {
            string expected = NormalizeFingerprint(expectedFingerprint);
            if (certificate == null || expected.Length != 64)
            {
                return false;
            }

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

function New-PinnedHttpClient {
    return [HermesRdp.PinnedHttpClientFactory]::Create(
        $script:ExpectedFingerprint
    )
}
'''
if old_function not in installer:
    raise SystemExit("PowerShell certificate callback anchor missing")
installer_path.write_text("\ufeff" + installer.replace(old_function, new_function, 1), encoding="utf-8")

runtime_test = '''$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$InstallerPath = Join-Path $PSScriptRoot '..\\scripts\\install-client.ps1'
$InstallerText = Get-Content -LiteralPath $InstallerPath -Raw
$Match = [regex]::Match(
    $InstallerText,
    "(?s)\\$PinnedHttpClientSource = @'\\r?\\n(.*?)\\r?\\n'@"
)
if (-not $Match.Success) {
    throw 'PinnedHttpClientSource was not found in install-client.ps1.'
}

if (-not ('HermesRdp.PinnedHttpClientFactory' -as [type])) {
    Add-Type `
        -TypeDefinition $Match.Groups[1].Value `
        -Language CSharp `
        -ReferencedAssemblies 'System.Net.Http.dll'
}

$Certificate = New-SelfSignedCertificate `
    -DnsName 'hermes-rdp-test.invalid' `
    -CertStoreLocation 'Cert:\\CurrentUser\\My'

try {
    $Sha = [Security.Cryptography.SHA256]::Create()
    try {
        $Expected = ([BitConverter]::ToString(
            $Sha.ComputeHash($Certificate.RawData)
        )).Replace('-', '')
    }
    finally {
        $Sha.Dispose()
    }

    if (-not [HermesRdp.PinnedHttpClientFactory]::ValidateCertificate(
        $Certificate,
        $Expected
    )) {
        throw 'Correct certificate fingerprint was rejected.'
    }

    if ([HermesRdp.PinnedHttpClientFactory]::ValidateCertificate(
        $Certificate,
        ('0' * 64)
    )) {
        throw 'Incorrect certificate fingerprint was accepted.'
    }

    $Client = [HermesRdp.PinnedHttpClientFactory]::Create($Expected)
    try {
        if ($Client.GetType().FullName -ne 'System.Net.Http.HttpClient') {
            throw 'Factory did not return HttpClient.'
        }
        if ([int]$Client.Timeout.TotalSeconds -ne 30) {
            throw 'Unexpected HttpClient timeout.'
        }
    }
    finally {
        $Client.Dispose()
    }
}
finally {
    Remove-Item -LiteralPath $Certificate.PSPath -Force -ErrorAction SilentlyContinue
}

Write-Host 'static-csharp-cert-pinning=PASS'
'''
(root / "tests/Test-PinnedHttpClient.ps1").write_text("\ufeff" + runtime_test, encoding="utf-8")

python_test = '''from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WindowsCertificatePinningTests(unittest.TestCase):
    def test_installer_uses_static_csharp_validator(self) -> None:
        text = (ROOT / "scripts/install-client.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("class PinnedHttpClientFactory", text)
        self.assertIn("ValidateCertificate", text)
        self.assertIn("ServerCertificateCustomValidationCallback = delegate", text)
        self.assertIn("[HermesRdp.PinnedHttpClientFactory]::Create", text)
        self.assertNotIn("$Handler.ServerCertificateCustomValidationCallback = {", text)
        self.assertNotIn("param($Request, $Certificate, $Chain, $SslPolicyErrors)", text)

    def test_windows_runtime_test_exists(self) -> None:
        text = (ROOT / "tests/Test-PinnedHttpClient.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("static-csharp-cert-pinning=PASS", text)
        self.assertIn("Correct certificate fingerprint was rejected", text)
        self.assertIn("Incorrect certificate fingerprint was accepted", text)


if __name__ == "__main__":
    unittest.main()
'''
(root / "tests/test_windows_cert_pinning.py").write_text(python_test, encoding="utf-8")

excluded = {
    Path("CHANGELOG.md"),
    Path("docs/releases/v1.0.0.md"),
    Path("docs/releases/v1.0.1.md"),
    Path("docs/releases/v1.0.2.md"),
    Path("docs/releases/v1.0.3.md"),
    Path("docs/releases/v1.0.4.md"),
    Path("docs/releases/v1.0.5.md"),
    Path("docs/releases/v1.0.6.md"),
    Path(".github/prepare_v1_0_7.py"),
    Path(".github/workflows/prepare-v1-0-7.yml"),
    Path(".github/workflows/ci.yml"),
}
allowed = {".md", ".py", ".toml", ".html", ".xml", ".txt", ".json", ".sh", ".js", ".css", ".yml", ".yaml"}
for path in root.rglob("*"):
    relative = path.relative_to(root)
    if not path.is_file() or ".git" in path.parts or relative in excluded:
        continue
    if path.name != "VERSION" and path.suffix.lower() not in allowed:
        continue
    data = path.read_text(encoding="utf-8")
    updated = data.replace("v" + old_version, "v" + new_version).replace(old_version, new_version)
    if updated != data:
        path.write_text(updated, encoding="utf-8")

(root / "VERSION").write_text(new_version + "\n", encoding="utf-8")

changelog_path = root / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
marker = "## [1.0.6] — 2026-08-06\n"
section = '''## [1.0.7] — 2026-08-06

Hotfix HTTPS certificate pinning в Windows PowerShell 5.1.

### Исправлено

- PowerShell scriptblock удалён из `ServerCertificateCustomValidationCallback`;
- проверка SHA-256 fingerprint выполняется статическим C# callback без зависимости от PowerShell runspace;
- сетевой запрос больше не завершается общей `HttpRequestException` при корректно доступном сервере;
- fingerprint pinning сохранён: неверный сертификат по-прежнему отклоняется;
- добавлен Windows runtime test с реальным самоподписанным сертификатом;
- добавлены Python regression tests, запрещающие возврат PowerShell callback.

### Совместимость

- API, SQLite registry, pairing contract, FRP и стандартные порты не изменены;
- `install-client.ps1` остаётся совместимым с Windows PowerShell 5.1.

'''
if marker not in changelog:
    raise SystemExit("CHANGELOG marker missing")
changelog = changelog.replace("Пока нет изменений после `v1.0.6`.", "Пока нет изменений после `v1.0.7`.")
changelog = changelog.replace(marker, section + marker, 1)
changelog = changelog.replace(
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.6...HEAD",
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.7...HEAD",
)
changelog = changelog.replace(
    "[1.0.6]: https://github.com/bakunity/RDP/releases/tag/v1.0.6",
    "[1.0.7]: https://github.com/bakunity/RDP/releases/tag/v1.0.7\n"
    "[1.0.6]: https://github.com/bakunity/RDP/releases/tag/v1.0.6",
)
changelog_path.write_text(changelog, encoding="utf-8")

notes = '''# Hermes RDP v1.0.7

Hotfix HTTPS certificate pinning для Windows PowerShell 5.1.

## Исправлено

`HttpClientHandler.ServerCertificateCustomValidationCallback` больше не использует PowerShell scriptblock. Ранее .NET вызывал этот callback на фоновом потоке без PowerShell runspace, из-за чего корректный HTTPS-запрос завершался `PSInvalidOperationException` и внешней `HttpRequestException`.

Проверка SHA-256 fingerprint перенесена в статический C# callback. Сертификат сервера по-прежнему принимается только при точном совпадении fingerprint.

## Проверки

- Windows runtime test создаёт реальный самоподписанный сертификат;
- правильный SHA-256 fingerprint принимается;
- неправильный fingerprint отклоняется;
- Linux release checks и PowerShell 5.1 parsing проходят.

## Совместимость

- API, SQLite registry, pairing contract, FRP и стандартные порты не изменены;
- Windows PowerShell 5.1 поддерживается.

## Ссылки

- [GitHub Release v1.0.7](https://github.com/bakunity/RDP/releases/tag/v1.0.7)
- [Тестирование от А до Я](https://github.com/bakunity/RDP/blob/v1.0.7/docs/TESTING_A_TO_Z.md)
'''
(root / "docs/releases/v1.0.7.md").write_text(notes, encoding="utf-8")

(root / ".github/prepare_v1_0_7.py").unlink()
(root / ".github/workflows/prepare-v1-0-7.yml").unlink()
