from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClientUpdateRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = (ROOT / "scripts/update-client.ps1").read_text(
            encoding="utf-8-sig"
        )

    def test_candidate_is_staged_and_parsed_before_runtime_stop(self) -> None:
        text = self.text
        download = text.index("Invoke-WebRequest")
        candidate_parse = text.index("ParseFile(\n        $CandidatePath")
        stop_task = text.index("Stop-ScheduledTask", candidate_parse)
        self.assertLess(download, candidate_parse)
        self.assertLess(candidate_parse, stop_task)
        self.assertIn("$CandidatePath", text)
        self.assertIn("Candidate parse error", text)

    def test_requested_ref_resolves_to_immutable_sha(self) -> None:
        text = self.text
        self.assertIn("function Resolve-RepositorySha", text)
        self.assertIn("^[0-9a-fA-F]{40}$", text)
        self.assertIn("https://api.github.com/repos/$Repo/commits/$Encoded", text)
        self.assertIn("$ResolvedSha/client/HermesRdpAgent.ps1", text)
        self.assertIn("resolved_sha = $ResolvedSha", text)

    def test_existing_identity_and_task_definition_are_not_recreated(self) -> None:
        text = self.text
        self.assertIn("Get-Content `\n        -LiteralPath $ConfigPath", text)
        self.assertIn("Export-ScheduledTask -TaskName $TaskName", text)
        self.assertNotIn("Register-ScheduledTask", text)
        self.assertNotIn("Unregister-ScheduledTask", text)
        self.assertNotIn("Set-Content -LiteralPath $ConfigPath", text)
        self.assertNotIn("ssh-keygen", text)
        self.assertNotIn("revoke-self", text)

    def test_update_has_bounded_runtime_readiness(self) -> None:
        text = self.text
        self.assertIn("$StartupTimeoutSeconds = 75", text)
        self.assertIn("$StartupStableSeconds = 20", text)
        self.assertIn("function Wait-HermesRuntimeReady", text)
        self.assertIn("$Agents.Count -eq 1", text)
        self.assertIn("$Ssh.Count -le 1", text)
        self.assertIn("-not $ExpectSsh -or $Ssh.Count -eq 1", text)
        self.assertIn("$Task.State -eq 'Running'", text)
        self.assertIn("Hermes runtime не вышел в стабильное состояние", text)

    def test_activation_failure_restores_previous_agent_and_restarts_task(self) -> None:
        text = self.text
        self.assertIn("$BackupAgent", text)
        self.assertIn("previous_agent_sha256", text)
        self.assertIn("candidate_agent_sha256", text)
        self.assertIn("Copy-Item `\n                -LiteralPath $BackupAgent", text)
        self.assertGreaterEqual(text.count("Start-ScheduledTask -TaskName $TaskName"), 2)
        self.assertIn("ROLLBACK=PASS", text)
        self.assertIn("ROLLBACK=FAIL", text)
        self.assertIn("предыдущий агент восстановлен", text)

    def test_unhealthy_prestate_is_refused_as_repair_case(self) -> None:
        text = self.text
        self.assertIn("$AgentsBefore.Count -ne 1", text)
        self.assertIn("$SshBefore.Count -gt 1", text)
        self.assertIn("Используйте repair flow", text)
        self.assertIn("$TaskBefore.State -eq 'Disabled'", text)

    def test_candidate_temp_file_is_cleaned(self) -> None:
        text = self.text
        self.assertIn("finally {", text)
        self.assertIn("-LiteralPath $CandidatePath", text)
        self.assertIn("-ErrorAction SilentlyContinue", text)


if __name__ == "__main__":
    unittest.main()
