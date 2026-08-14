from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AutomaticCertificateRotationTests(unittest.TestCase):
    def test_server_publishes_only_non_secret_certificate_state(self) -> None:
        state = (ROOT / "server/bin/hermes-rdp-cert-state-refresh.sh").read_text(
            encoding="utf-8"
        )
        for marker in (
            "trusted-rdp-cert-state.json",
            "openssl x509 -in \"$CERT\" -noout -checkip \"$CERT_NAME\"",
            "-fingerprint -sha1",
            "-fingerprint -sha256",
            "chown root:hermes-rdp",
            "chmod 0640",
            "CERT_STATE=REFRESHED",
        ):
            self.assertIn(marker, state)
        self.assertNotIn("privkey.pem", state)
        self.assertNotIn("pkcs12", state)
        self.assertNotIn("password", state.lower())

        renew = (ROOT / "server/bin/hermes-rdp-cert-renew.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("STATE_REFRESH=/usr/local/sbin/hermes-rdp-cert-state-refresh", renew)
        certbot_call = renew.index('"$CERTBOT" renew')
        refresh_call = renew.index('"$STATE_REFRESH" >/dev/null')
        self.assertLess(certbot_call, refresh_call)
        self.assertIn("exec 9>", renew)
        self.assertIn("flock -w 300 9", renew)

    def test_status_endpoint_authenticates_and_never_invokes_package_helper(self) -> None:
        api = (ROOT / "server/hermes_rdp/api.py").read_text(encoding="utf-8")
        self.assertIn('action == "rdp-certificate-status"', api)
        start = api.index("    def _rdp_certificate_status")
        end = api.index("    def _rdp_certificate(self", start)
        method = api[start:end]
        self.assertLess(method.index("self._device_auth(device_id)"), method.index("CERT_STATE_FILE"))
        self.assertIn("HTTPStatus.UNAUTHORIZED", method)
        self.assertIn("thumbprint", method)
        self.assertNotIn("subprocess.run", method)
        self.assertNotIn("pfx_base64", method)
        self.assertNotIn("password", method)

    def test_windows_worker_checks_status_before_full_sync(self) -> None:
        worker = (ROOT / "client/HermesRdpCertRotation.ps1").read_text(
            encoding="utf-8-sig"
        )
        for marker in (
            "RotationPinnedHttpClientFactory",
            "api_fingerprint",
            "device_token",
            "/rdp-certificate-status",
            "SSLCertificateSHA1HashType",
            "$BeforeType -eq 3 -and $BeforeHash -eq $Expected",
            "CERT_ROTATION=UNCHANGED",
            "Invoke-CertificateSync",
            "CERT_ROTATION=UPDATED",
            "Global\\HermesRdpCertificateRotation",
            "IntervalSeconds = 900",
        ):
            self.assertIn(marker, worker)
        self.assertLess(
            worker.index("$BeforeType -eq 3 -and $BeforeHash -eq $Expected"),
            worker.index("Invoke-CertificateSync\n"),
        )
        self.assertNotIn("pfx_base64", worker)
        self.assertNotIn("Import-PfxCertificate", worker)

    def test_rotation_setup_is_system_startup_transactional_and_immutable(self) -> None:
        setup = (ROOT / "scripts/setup-client-cert-rotation.ps1").read_text(
            encoding="utf-8-sig"
        )
        for marker in (
            "Resolve-RepositorySha",
            "$ResolvedSha/client/HermesRdpCertRotation.ps1",
            "$ResolvedSha/scripts/sync-rdp-certificate.ps1",
            "Assert-PowerShellFile",
            "Set-SystemScriptAcl",
            "New-ScheduledTaskTrigger -AtStartup",
            "-UserId 'SYSTEM'",
            "-RunLevel Highest",
            "RestartCount 999",
            "CERT-012_SETUP=PASS",
            "CERT-012_SETUP_ROLLBACK=PASS",
        ):
            self.assertIn(marker, setup)
        self.assertLess(setup.index("Assert-PowerShellFile"), setup.index("Register-RotationTask"))

    def test_server_setup_installs_and_refreshes_state(self) -> None:
        setup = (ROOT / "scripts/setup-trusted-rdp-cert.sh").read_text(
            encoding="utf-8"
        )
        for marker in (
            "hermes-rdp-cert-state-refresh.sh",
            "/usr/local/sbin/hermes-rdp-cert-state-refresh",
            "trusted-rdp-cert-state.json",
            "'state_file': state_file",
            "certificate_state=READY",
        ):
            self.assertIn(marker, setup)

    def test_server_update_and_uninstall_manage_state_helper_transactionally(self) -> None:
        updater = (ROOT / "scripts/update-server.sh").read_text(encoding="utf-8")
        uninstall = (ROOT / "scripts/uninstall-server.sh").read_text(encoding="utf-8")

        for marker in (
            "server/bin/hermes-rdp-cert-renew.sh",
            "server/bin/hermes-rdp-cert-state-refresh.sh",
            "/usr/local/sbin/hermes-rdp-cert-renew",
            "/usr/local/sbin/hermes-rdp-cert-state-refresh",
            "/etc/hermes-rdp/trusted-rdp-cert-state.json",
        ):
            self.assertIn(marker, updater)

        self.assertIn(
            "restore_optional_file /usr/local/sbin/hermes-rdp-cert-renew",
            updater,
        )
        self.assertIn(
            "restore_optional_file /usr/local/sbin/hermes-rdp-cert-state-refresh",
            updater,
        )
        self.assertIn(
            "restore_optional_file /etc/hermes-rdp/trusted-rdp-cert-state.json",
            updater,
        )
        self.assertIn(
            "/usr/local/sbin/hermes-rdp-cert-state-refresh >/dev/null",
            updater,
        )
        self.assertIn("/usr/local/sbin/hermes-rdp-cert-state-refresh", uninstall)
        self.assertIn("Data, configuration and ACME certificate lineage were preserved", uninstall)


if __name__ == "__main__":
    unittest.main()
