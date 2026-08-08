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

    def test_agent_classifies_rdp_channel_without_public_endpoint_probe(self) -> None:
        text = (ROOT / "client/HermesRdpAgent.ps1").read_text(encoding="utf-8-sig")
        self.assertIn("function Get-RdpConnectionSummary", text)
        self.assertIn("rdp_hermes_connections", text)
        self.assertIn("rdp_direct_connections", text)
        self.assertIn("rdp_other_local_connections", text)
        self.assertIn("$HermesSshPids", text)
        self.assertIn("OwningProcess", text)
        self.assertIn("127.0.0.1", text)
        self.assertIn("::1", text)
        self.assertNotIn("function Test-TcpPort", text)
        self.assertNotIn("$EndpointAvailable", text)

    def test_dashboard_separates_control_states(self) -> None:
        text = (ROOT / "server/hermes_rdp/bot.py").read_text(encoding="utf-8")
        for value in (
            "Агент:",
            "RDP-доступ (цель):",
            "Агент применил:",
            "SSH-туннель:",
            "Публичный RDP:",
            "RDP через Hermes:",
            "RDP напрямую (LAN/VPN):",
            "В СЕТИ",
            "НЕ В СЕТИ",
            "ПОДКЛЮЧЕН",
            "ОТКЛЮЧЕН",
            "ОТКРЫТ",
            "ЗАКРЫТ",
            "НЕИЗВЕСТНО",
            "ДУБЛИ",
            "НЕСООТВЕТСТВИЕ",
            "Последняя команда:",
            "ВКЛЮЧИТЬ ДОСТУП",
            "ВЫКЛЮЧИТЬ ДОСТУП",
            "КОМАНДА ВЫПОЛНЯЕТСЯ",
            "ПЕРЕЗАПУСК",
            "ОБНОВИТЬ",
            "АВТО 3с",
        ):
            self.assertIn(value, text)
        for value in (
            "ONLINE",
            "OFFLINE",
            "CONNECTED",
            "DISCONNECTED",
            "OPEN",
            "CLOSED",
            "UNKNOWN",
            "MULTIPLE",
            "INCONSISTENT",
            "REFRESH",
            "RESTART",
            "LIVE 3s",
        ):
            self.assertNotIn(value, text)
        self.assertNotIn("Внешние клиенты:", text)
        self.assertNotIn("RDP-соединений:", text)

    def test_bot_does_not_split_desired_state_from_queue(self) -> None:
        text = (ROOT / "server/hermes_rdp/bot.py").read_text(encoding="utf-8")
        start = text.index('if data.startswith("cmd:")')
        end = text.index('if data.startswith("delete:")', start)
        block = text[start:end]
        self.assertIn("self.registry.queue_command(device_id, action)", block)
        self.assertNotIn("set_enabled", block)

    def test_completed_result_keeps_action(self) -> None:
        text = (ROOT / "server/hermes_rdp/db.py").read_text(encoding="utf-8")
        self.assertIn('"action": str(row["pending_command"] or "")', text)


if __name__ == "__main__":
    unittest.main()