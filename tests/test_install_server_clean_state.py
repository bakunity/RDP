from pathlib import Path
import unittest


class CleanInstallOpenSshTests(unittest.TestCase):
    def test_install_generates_dedicated_host_key_and_restricts_tunnel_user(self) -> None:
        text = Path('scripts/install-server.sh').read_text(encoding='utf-8')
        self.assertIn('SSH_HOST_KEY=/etc/hermes-rdp/ssh_host_ed25519_key', text)
        self.assertIn("ssh-keygen -q -t ed25519", text)
        self.assertIn('PasswordAuthentication no', text)
        self.assertIn('MaxSessions 0', text)
        self.assertIn('AuthorizedKeysFile none', text)
        self.assertNotIn('FRP_LINUX_SHA256', text)

    def test_migration_requires_explicit_flag_and_removes_legacy_service(self) -> None:
        text = Path('scripts/install-server.sh').read_text(encoding='utf-8')
        self.assertIn('Existing Hermes FRP service detected.', text)
        self.assertIn('Re-run with --migrate', text)
        self.assertIn('systemctl disable --now frps.service', text)
        self.assertIn('rm -f /etc/systemd/system/frps.service /usr/local/bin/frps', text)


if __name__ == '__main__':
    unittest.main()
