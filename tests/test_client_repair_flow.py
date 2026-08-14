from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClientRepairFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # CERT-013 deliberately preserves the previously live-accepted Repair
        # implementation byte-for-byte as repair-client-core.ps1. Keep all
        # historical Repair invariants attached to that core; lifecycle wrapper
        # composition/rollback is covered separately by the CERT-013 suite.
        cls.text = (ROOT / "scripts/repair-client-core.ps1").read_text(
            encoding="utf-8-sig"
        )

    def test_repair_is_not_fresh_pairing_or_rekey(self) -> None:
        text = self.text
        self.assertNotIn("/v1/pair", text)
        self.assertNotIn("revoke-self", text)
        self.assertNotIn("PairCode", text)
        self.assertNotIn("'-t'\n", text)
        self.assertNotIn("Set-MpPreference", text)
        self.assertNotIn("Add-MpPreference", text)
        self.assertIn("Repair не создаёт новую identity", text)
        self.assertIn("server-authorized rekey flow", text)

    def test_expected_device_guard_prevents_wrong_machine_repair(self) -> None:
        text = self.text
        self.assertIn("[string]$ExpectedDeviceId", text)
        self.assertIn("$DeviceId -ne $ExpectedDeviceId", text)
        self.assertIn("Эта команда предназначена для другого Hermes-устройства", text)

    def test_existing_identity_and_trust_anchor_are_required(self) -> None:
        text = self.text
        self.assertIn("$ConfigPath = Join-Path $BaseDir 'device.json'", text)
        self.assertIn("$DeviceToken = [string]$Config.device_token", text)
        self.assertIn("$KeyPath = [string]$Config.ssh_key_path", text)
        self.assertIn("$KnownHostsPath = [string]$Config.known_hosts_path", text)
        self.assertIn("Приватный SSH-ключ Hermes отсутствует", text)
        self.assertIn("known_hosts Hermes отсутствует", text)
        self.assertIn("Get-Sha256 -Path $ConfigPath", text)
        self.assertIn("Get-Sha256 -Path $KeyPath", text)
        self.assertIn("Get-Sha256 -Path $PublicKeyPath", text)
        self.assertIn("Get-Sha256 -Path $KnownHostsPath", text)
        self.assertNotIn("Set-Content -LiteralPath $ConfigPath", text)

    def test_private_public_key_pair_is_verified_without_rotation(self) -> None:
        text = self.text
        self.assertIn("& $KeygenPath -y -f $KeyPath", text)
        self.assertIn("$StoredPublicParts[1] -ne $DerivedPublicParts[1]", text)
        self.assertIn("private/public key не соответствуют", text)

    def test_x86_powershell_uses_sysnative_for_native_openssh(self) -> None:
        text = self.text
        self.assertIn("[Environment]::Is64BitOperatingSystem", text)
        self.assertIn("[Environment]::Is64BitProcess", text)
        self.assertIn("Join-Path $env:WINDIR 'Sysnative'", text)
        self.assertIn("OpenSSH\\ssh.exe", text)
        self.assertIn("OpenSSH\\ssh-keygen.exe", text)

    def test_api_is_pinned_and_existing_token_is_authenticated_before_mutation(self) -> None:
        text = self.text
        health = text.index("$Health = $Http.GetStringAsync")
        probe = text.index("$Probe = Invoke-PinnedPost")
        resolve = text.index("$ResolvedSha = Resolve-RepositorySha")
        stop = text.index("Stop-ScheduledTask", resolve)
        self.assertLess(health, probe)
        self.assertLess(probe, resolve)
        self.assertLess(resolve, stop)
        self.assertIn("RepairPinnedHttpClientFactory", text)
        self.assertIn("$ApiBase/v1/devices/$DeviceId/telemetry", text)
        self.assertIn("-Token $DeviceToken", text)
        self.assertIn("repair_probe = $true", text)
        self.assertIn("$DesiredEnabled = [bool]$Probe.desired_enabled", text)

    def test_candidate_is_staged_and_parsed_before_runtime_stop(self) -> None:
        text = self.text
        download = text.index("-OutFile $CandidatePath")
        parse = text.index("ParseFile(\n        $CandidatePath")
        stop = text.index("Stop-ScheduledTask", parse)
        self.assertLess(download, parse)
        self.assertLess(parse, stop)
        self.assertIn("$ResolvedSha/client/HermesRdpAgent.ps1", text)

    def test_repair_can_rebuild_missing_or_disabled_task(self) -> None:
        text = self.text
        self.assertIn("$TaskExistedBefore = $null -ne $TaskBefore", text)
        self.assertIn("function Register-CanonicalTask", text)
        self.assertIn("Register-ScheduledTask `", text)
        self.assertIn("-UserId 'SYSTEM'", text)
        self.assertIn("$Trigger.Delay = 'PT20S'", text)
        self.assertIn("-RestartCount 999", text)

    def test_bounded_readiness_uses_server_desired_state(self) -> None:
        text = self.text
        self.assertIn("$StartupTimeoutSeconds = 75", text)
        self.assertIn("$StartupStableSeconds = 20", text)
        self.assertIn("function Wait-HermesRuntimeReady", text)
        self.assertIn("$ExpectedSshCount = if ($DesiredEnabled) { 1 } else { 0 }", text)
        self.assertIn("$Agents.Count -eq 1", text)
        self.assertIn("$Ssh.Count -eq $ExpectedSshCount", text)
        self.assertIn("Control poll error:", text)
        self.assertIn("REPAIR=PASS", text)

    def test_repair_restores_rdp_runtime_without_defender_weakening(self) -> None:
        text = self.text
        self.assertIn("fDenyTSConnections", text)
        self.assertIn("Get-NetFirewallRule", text)
        self.assertIn("Set-Service -Name TermService -StartupType Automatic", text)
        self.assertIn("Start-Service -Name TermService", text)
        self.assertNotIn("DisableRealtimeMonitoring", text)
        self.assertNotIn("ExclusionPath", text)

    def test_failure_restores_previous_agent_and_task_snapshot(self) -> None:
        text = self.text
        self.assertIn("backups\\repairs", text)
        self.assertIn("repair-metadata.json", text)
        self.assertIn("$AgentExistedBefore", text)
        self.assertIn("$TaskXmlBefore", text)
        self.assertIn("Copy-Item `\n                    -LiteralPath $BackupAgent", text)
        self.assertIn("Register-ScheduledTask `\n                    -TaskName $TaskName `\n                    -Xml $TaskXmlBefore", text)
        self.assertIn("Unregister-ScheduledTask", text)
        self.assertIn("ROLLBACK=PASS", text)
        self.assertIn("ROLLBACK=FAIL", text)


if __name__ == "__main__":
    unittest.main()
