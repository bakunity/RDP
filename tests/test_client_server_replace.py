from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_ps(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class ClientServerReplaceTests(unittest.TestCase):
    def test_accepted_installer_is_preserved_as_core(self) -> None:
        core = ROOT / "scripts/install-client-core.ps1"
        self.assertTrue(core.is_file())
        self.assertEqual(
            git_blob_sha(core),
            "5eef32da26da79e0c56809c45cf7cc13bc7937ed",
        )

    def test_wrapper_uses_immutable_core_and_same_parameter_contract(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        for marker in (
            "[string]$Server",
            "[string]$PairCode",
            "[string]$Fingerprint",
            "[int]$ApiPort = 7443",
            "[string]$RepositoryRef = 'main'",
            "Resolve-RepositorySha",
            "$ResolvedSha/scripts/install-client-core.ps1",
            "Assert-PowerShellFile -Path $CoreCandidate",
            "RepositoryRef = $ResolvedSha",
        ):
            self.assertIn(marker, wrapper)

    def test_same_server_keeps_existing_repair_update_guard(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        self.assertIn("$SameServer", wrapper)
        self.assertIn("подключён к этому ", wrapper)
        self.assertIn("серверу (RDP-порт", wrapper)
        self.assertIn("repair/update", wrapper)
        same = wrapper.index("if ($SameServer)")
        prompt = wrapper.index("Введите REPLACE")
        self.assertLess(same, prompt)

    def test_different_server_requires_explicit_replace_and_new_identity(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        for marker in (
            "=== HERMES RDP SERVER REPLACE ===",
            "Введите REPLACE для переподключения к новому серверу",
            "Move-Item -LiteralPath $BaseDir -Destination $BackupDir",
            "Remove-HermesTask -TaskName $AgentTaskName",
            "Remove-HermesTask -TaskName $RotationTaskName",
            "& $CoreCandidate @CoreParams",
            "REPLACE=PASS",
        ):
            self.assertIn(marker, wrapper)

        move_old = wrapper.index(
            "Move-Item -LiteralPath $BaseDir -Destination $BackupDir"
        )
        run_core = wrapper.index("& $CoreCandidate @CoreParams")
        self.assertLess(move_old, run_core)

    def test_old_registration_is_revoked_only_after_new_core_succeeds(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        run_core = wrapper.index("& $CoreCandidate @CoreParams")
        revoke = wrapper.index(
            "$OldRevoke = Invoke-PinnedRevoke -Config $ExistingConfig"
        )
        self.assertLess(run_core, revoke)
        self.assertIn("HermesRdpReplace.PinnedHttpClientFactory", wrapper)
        self.assertIn("/revoke-self", wrapper)
        self.assertIn("client-replaced-server", wrapper)

    def test_replace_failure_restores_old_files_and_tasks(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        for marker in (
            "Get-TaskSnapshot -TaskName $AgentTaskName",
            "Get-TaskSnapshot -TaskName $RotationTaskName",
            "Restore-TaskSnapshot",
            "Move-Item -LiteralPath $BackupDir -Destination $BaseDir",
            "REPLACE_ROLLBACK=PASS",
        ):
            self.assertIn(marker, wrapper)

        rollback = wrapper.index("REPLACE_ROLLBACK=PASS")
        old_revoke = wrapper.index("$OldRevoke = Invoke-PinnedRevoke")
        self.assertGreater(rollback, old_revoke)

    def test_old_revoke_failure_does_not_break_new_install(self) -> None:
        wrapper = read_ps("scripts/install-client.ps1")
        self.assertIn("Старый сервер недоступен", wrapper)
        self.assertIn("Новый Hermes ", wrapper)
        self.assertIn("уже работает; удали", wrapper)
        self.assertIn("OLD_REGISTRATION=$OldRevoke", wrapper)


if __name__ == "__main__":
    unittest.main()
