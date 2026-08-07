from __future__ import annotations

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
