from __future__ import annotations

from pathlib import Path


def read(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8-sig" if p.suffix == ".ps1" else "utf-8")


def write(path: str, text: str) -> None:
    p = Path(path)
    p.write_text(text, encoding="utf-8-sig" if p.suffix == ".ps1" else "utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"pattern not found in {path}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


replace_once(
    "client/HermesRdpAgent.ps1",
    """function Get-SshProcesses {
    return @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.Name -eq 'ssh.exe' -and
                $_.CommandLine -and
                $_.CommandLine.Contains([string]$Config.ssh_key_path) -and
                $_.CommandLine.Contains(
                    \"0.0.0.0:$($Config.rdp_port):127.0.0.1:3389\"
                )
            }
    )
}""",
    """function Get-SshProcesses {
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
}""",
)

replace_once(
    "client/HermesRdpAgent.ps1",
    """    $Uptime = [int]((Get-Date) - $Boot).TotalSeconds
    $TunnelRunning = (Get-SshProcesses).Count -gt 0
    $EndpointAvailable = Test-TcpPort `""",
    """    $Uptime = [int]((Get-Date) - $Boot).TotalSeconds
    $State = Get-AgentState
    $SshProcesses = @(Get-SshProcesses)
    $TunnelRunning = $SshProcesses.Count -gt 0
    $EndpointAvailable = Test-TcpPort `""",
)

replace_once(
    "client/HermesRdpAgent.ps1",
    """        route = Get-RouteName
        ssh_tunnel_running = $TunnelRunning
        endpoint_available = [bool]$EndpointAvailable""",
    """        route = Get-RouteName
        access_enabled = [bool]$State.enabled
        ssh_tunnel_running = $TunnelRunning
        ssh_process_count = [int]$SshProcesses.Count
        endpoint_available = [bool]$EndpointAvailable""",
)

replace_once(
    "scripts/install-client.ps1",
    """function Ensure-OpenSshClient {
    $SshPath = Join-Path $env:WINDIR 'System32\\OpenSSH\\ssh.exe'
    $KeygenPath = Join-Path $env:WINDIR 'System32\\OpenSSH\\ssh-keygen.exe'
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
}""",
    """function Ensure-OpenSshClient {
    $CanonicalSystem32 = Join-Path $env:WINDIR 'System32'
    $NativeSystem32 = $CanonicalSystem32
    if (
        [Environment]::Is64BitOperatingSystem -and
        -not [Environment]::Is64BitProcess
    ) {
        # A 32-bit PowerShell process is redirected away from real x64
        # System32. Sysnative is the supported alias to reach native tools.
        $NativeSystem32 = Join-Path $env:WINDIR 'Sysnative'
    }

    $SshPath = Join-Path $CanonicalSystem32 'OpenSSH\\ssh.exe'
    $ProbeSshPath = Join-Path $NativeSystem32 'OpenSSH\\ssh.exe'
    $KeygenPath = Join-Path $NativeSystem32 'OpenSSH\\ssh-keygen.exe'

    if (
        (Test-Path -LiteralPath $ProbeSshPath) -and
        (Test-Path -LiteralPath $KeygenPath)
    ) {
        return @{
            # Keep the canonical path in device.json. Scheduled Task runs in
            # the native environment where Sysnative is not a real directory.
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
        $InstallResult = Add-WindowsCapability `
            -Online `
            -Name $Capability.Name
        if ($InstallResult.RestartNeeded) {
            Write-Host 'Windows сообщает, что для OpenSSH требуется перезагрузка.'
        }
    }

    if (
        -not (Test-Path -LiteralPath $ProbeSshPath) -or
        -not (Test-Path -LiteralPath $KeygenPath)
    ) {
        throw (
            'OpenSSH Client отмечен как установлен, но системные ' +
            'ssh.exe/ssh-keygen.exe не найдены.'
        )
    }

    return @{
        ssh = $SshPath
        keygen = $KeygenPath
    }
}""",
)

replace_once(
    "server/hermes_rdp/db.py",
    """        result = {
            \"seq\": int(seq),
            \"ok\": bool(ok),
            \"message\": str(message)[:500],
            \"completed_at\": now(),
        }
        with self.connect() as conn:
            row = conn.execute(
                \"SELECT command_seq FROM devices WHERE id=?\", (device_id,)
            ).fetchone()""",
    """        with self.connect() as conn:
            row = conn.execute(
                \"SELECT command_seq,pending_command FROM devices WHERE id=?\",
                (device_id,),
            ).fetchone()
            result = {
                \"seq\": int(seq),
                \"action\": str(row[\"pending_command\"] or \"\") if row else \"\",
                \"ok\": bool(ok),
                \"message\": str(message)[:500],
                \"completed_at\": now(),
            }""",
)

replace_once(
    "server/hermes_rdp/bot.py",
    "from .tunnel import close_tunnel\nfrom .tunnel import close_tunnel\n",
    "from .tunnel import close_tunnel\n",
)

replace_once(
    "server/hermes_rdp/bot.py",
    """        ssh_tunnel = telemetry.get(\"ssh_tunnel_running\", False)
        endpoint = telemetry.get(\"endpoint_available\", False)
        text = (""",
    """        ssh_tunnel = bool(telemetry.get(\"ssh_tunnel_running\", False))
        endpoint = bool(telemetry.get(\"endpoint_available\", False))
        access_enabled = bool(device.get(\"enabled\", True))
        pending_action = str(device.get(\"pending_command\") or \"\")
        last_result = device.get(\"last_result\") or {}
        action_names = {
            \"on\": \"включение доступа\",
            \"off\": \"выключение доступа\",
            \"restart\": \"перезапуск туннеля\",
        }
        if pending_action:
            command_line = (
                \"⏳ Команда: \"
                + action_names.get(pending_action, pending_action)
                + \"…\"
            )
        elif last_result:
            result_icon = \"✅\" if last_result.get(\"ok\") else \"❌\"
            result_action = action_names.get(
                str(last_result.get(\"action\") or \"\"),
                \"последняя команда\",
            )
            command_line = f\"{result_icon} Последняя команда: {result_action}\"
        else:
            command_line = \"Последняя команда: —\"
        text = (""",
)

replace_once(
    "server/hermes_rdp/bot.py",
    """            f\"SSH-туннель: {'работает' if ssh_tunnel else 'остановлен'}\\n\"
            f\"Endpoint: {'доступен' if endpoint else 'закрыт'}\\n\"
            f\"RDP-соединений: {int(telemetry.get('rdp_connections', 0) or 0)}\\n\"
            f\"Внешние клиенты: {escape(', '.join(telemetry.get('rdp_remote_addresses') or []) or 'нет')}\\n\"
            f\"Сессии: {escape(', '.join(sessions) or 'нет')}\\n\"""",
    """            \"СОСТОЯНИЕ\\n\"
            f\"Агент: {'🟢 ONLINE' if online else '🔴 OFFLINE'}\\n\"
            f\"RDP-доступ: {'🟢 ВКЛЮЧЕН' if access_enabled else '⚪ ВЫКЛЮЧЕН'}\\n\"
            f\"SSH-туннель: {'🟢 CONNECTED' if ssh_tunnel else '⚪ DISCONNECTED'}\\n\"
            f\"Endpoint: {'🟢 OPEN' if endpoint else '⚪ CLOSED'}\\n\"
            f\"RDP-соединений: {int(telemetry.get('rdp_connections', 0) or 0)}\\n\"
            f\"{command_line}\\n\"
            f\"Сессии Windows: {escape(', '.join(sessions) or 'нет')}\\n\"""",
)

replace_once(
    "server/hermes_rdp/bot.py",
    """        keyboard = {
            \"inline_keyboard\": [
                [
                    {\"text\": \"🟢 ON\", \"callback_data\": f\"cmd:on:{device['id']}\"},
                    {\"text\": \"🔴 OFF\", \"callback_data\": f\"cmd:off:{device['id']}\"},
                    {\"text\": \"♻️ RESTART\", \"callback_data\": f\"cmd:restart:{device['id']}\"},
                ],
                [
                    {\"text\": \"🔄 REFRESH\", \"callback_data\": \"refresh\"},
                    {
                        \"text\": \"⏸ LIVE 3s\"
                        if self.registry.get_setting(\"live\", \"1\") == \"1\"
                        else \"▶️ LIVE 3s\",
                        \"callback_data\": \"live\",
                    },
                ],
                [
                    {\"text\": \"🗑 УДАЛИТЬ\", \"callback_data\": f\"delete:{device['id']}\"},
                    {\"text\": \"⬅️ К СПИСКУ\", \"callback_data\": \"home\"},
                ],
            ]
        }""",
    """        if pending_action:
            control_rows = [
                [{\"text\": \"⏳ КОМАНДА ВЫПОЛНЯЕТСЯ\", \"callback_data\": \"refresh\"}]
            ]
        elif access_enabled:
            control_rows = [[
                {\"text\": \"🔴 ВЫКЛЮЧИТЬ ДОСТУП\", \"callback_data\": f\"cmd:off:{device['id']}\"},
                {\"text\": \"♻️ RESTART\", \"callback_data\": f\"cmd:restart:{device['id']}\"},
            ]]
        else:
            control_rows = [[
                {\"text\": \"🟢 ВКЛЮЧИТЬ ДОСТУП\", \"callback_data\": f\"cmd:on:{device['id']}\"},
            ]]
        keyboard = {
            \"inline_keyboard\": control_rows + [
                [
                    {\"text\": \"🔄 REFRESH\", \"callback_data\": \"refresh\"},
                    {
                        \"text\": \"⏸ LIVE 3s\"
                        if self.registry.get_setting(\"live\", \"1\") == \"1\"
                        else \"▶️ LIVE 3s\",
                        \"callback_data\": \"live\",
                    },
                ],
                [
                    {\"text\": \"🗑 УДАЛИТЬ\", \"callback_data\": f\"delete:{device['id']}\"},
                    {\"text\": \"⬅️ К СПИСКУ\", \"callback_data\": \"home\"},
                ],
            ]
        }""",
)

replace_once(
    "server/hermes_rdp/bot.py",
    """                device = self.registry.get_device(device_id)
                self.registry.set_enabled(device_id, action != \"off\")
                self.registry.queue_command(device_id, action)""",
    """                device = self.registry.get_device(device_id)
                if device.get(\"pending_command\"):
                    raise ValueError(\"Предыдущая команда ещё выполняется\")
                self.registry.set_enabled(device_id, action != \"off\")
                self.registry.queue_command(device_id, action)""",
)

Path("tests/test_control_state_dashboard.py").write_text(
    '''from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ControlStateDashboardTests(unittest.TestCase):
    def test_agent_uses_unique_key_path_for_ssh_identity(self) -> None:
        text = (ROOT / "client/HermesRdpAgent.ps1").read_text(encoding="utf-8-sig")
        start = text.index("function Get-SshProcesses")
        end = text.index("function Start-SshTunnel", start)
        block = text[start:end]
        self.assertIn("$KeyPath", block)
        self.assertIn("Contains($KeyPath)", block)
        self.assertNotIn("0.0.0.0:$($Config.rdp_port):127.0.0.1:3389", block)
        self.assertIn("access_enabled", text)
        self.assertIn("ssh_process_count", text)

    def test_dashboard_separates_control_states(self) -> None:
        text = (ROOT / "server/hermes_rdp/bot.py").read_text(encoding="utf-8")
        for value in (
            "Агент:",
            "RDP-доступ:",
            "SSH-туннель:",
            "Endpoint:",
            "Последняя команда:",
            "ВКЛЮЧИТЬ ДОСТУП",
            "ВЫКЛЮЧИТЬ ДОСТУП",
            "КОМАНДА ВЫПОЛНЯЕТСЯ",
        ):
            self.assertIn(value, text)
        self.assertNotIn("Внешние клиенты:", text)

    def test_completed_result_keeps_action(self) -> None:
        text = (ROOT / "server/hermes_rdp/db.py").read_text(encoding="utf-8")
        self.assertIn('"action": str(row["pending_command"] or "")', text)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

Path("tests/test_windows_native_openssh.py").write_text(
    '''from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WindowsNativeOpenSshTests(unittest.TestCase):
    def test_x86_powershell_uses_sysnative_probe(self) -> None:
        text = (ROOT / "scripts/install-client.ps1").read_text(encoding="utf-8-sig")
        for value in (
            "Is64BitOperatingSystem",
            "Is64BitProcess",
            "Sysnative",
            "$CanonicalSystem32",
            "$ProbeSshPath",
        ):
            self.assertIn(value, text)
        self.assertIn("ssh = $SshPath", text)
        self.assertIn("keygen = $KeygenPath", text)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)

Path(".github/workflows/apply-control-state-fix.yml").unlink(missing_ok=True)
Path("scripts/_apply_control_state_patch.py").unlink(missing_ok=True)
