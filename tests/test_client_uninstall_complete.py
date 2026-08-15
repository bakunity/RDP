from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_ps(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


class ClientUninstallCompleteTests(unittest.TestCase):
    def test_cert_setup_preserves_first_pre_hermes_binding(self) -> None:
        setup = read_ps("scripts/setup-client-cert-rotation.ps1")
        for marker in (
            "$OriginPath = Join-Path $BaseDir 'rdp-certificate-origin.json'",
            "$LegacyBackupPath = Join-Path $BaseDir 'rdp-certificate-backup.json'",
            "function Initialize-RdpOriginSnapshot",
            "original_thumbprint",
            "original_hash_type",
            "Source = 'CURRENT_LISTENER'",
            "Source = 'LEGACY_BACKUP'",
            "return 'PRESERVED'",
            "$OriginState = Initialize-RdpOriginSnapshot",
            'Write-Host "RDP_ORIGIN=$OriginState"',
        ):
            self.assertIn(marker, setup)

        init = setup.index("$OriginState = Initialize-RdpOriginSnapshot")
        first_sync = setup.index("-File $WorkerPath", init)
        self.assertLess(init, first_sync)

    def test_uninstall_restores_listener_before_revoking_device(self) -> None:
        script = read_ps("scripts/uninstall-client.ps1")
        for marker in (
            "=== HERMES RDP UNINSTALL ===",
            "function Get-RdpOriginSnapshot",
            "function Restore-RdpBinding",
            "PASS_$($RollbackSnapshot.Source)",
            "Hermes trusted RDP certificate активен, но rollback snapshot не найден",
            "HermesRdpUninstall.PinnedHttpClientFactory",
            "/revoke-self",
            "client-uninstall",
            "SERVER_REVOKE=$ServerRevoke",
            "LOCAL_STATE=REMOVED",
            "RDP_3389=LISTEN",
            "UNINSTALL=PASS",
        ):
            self.assertIn(marker, script)

        restore = script.index("$RestoredThumbprint = Restore-RdpBinding")
        revoke = script.index("$ServerRevoke = Invoke-PinnedRevoke")
        delete_state = script.index("if (Test-Path -LiteralPath $BaseDir) {", revoke)
        self.assertLess(restore, revoke)
        self.assertLess(revoke, delete_state)

    def test_uninstall_removes_active_state_instead_of_secret_archive(self) -> None:
        script = read_ps("scripts/uninstall-client.ps1")
        self.assertNotIn(".removed.", script)
        self.assertIn("-LiteralPath $BaseDir", script)
        self.assertIn("-Recurse", script)
        self.assertIn("-Force", script)
        self.assertIn("LOCAL_TASKS=ABSENT", script)
        self.assertIn("HERMES_PROCESSES=0", script)

    def test_server_revoke_failure_is_nonfatal_to_local_cleanup(self) -> None:
        script = read_ps("scripts/uninstall-client.ps1")
        self.assertIn("if ($ServerRevoke -ne 'REVOKED')", script)
        self.assertIn("Локальные credentials будут", script)
        warning = script.index("if ($ServerRevoke -ne 'REVOKED')")
        delete_state = script.index("if (Test-Path -LiteralPath $BaseDir) {", warning)
        self.assertLess(warning, delete_state)

    def test_uninstall_retains_cert013_task_and_worker_cleanup_markers(self) -> None:
        script = read_ps("scripts/uninstall-client.ps1")
        for marker in (
            "$RotationTaskName = 'Hermes RDP Certificate Rotation'",
            "$RotationPath = Join-Path $BaseDir 'HermesRdpCertRotation.ps1'",
            "@($TaskName, $RotationTaskName)",
            "Stop-ScheduledTask",
            "Unregister-ScheduledTask",
            "$_.CommandLine.Contains($RotationPath)",
        ):
            self.assertIn(marker, script)


if __name__ == "__main__":
    unittest.main()
