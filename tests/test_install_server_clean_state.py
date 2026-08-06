from pathlib import Path
import unittest


class CleanInstallTokenMigrationTests(unittest.TestCase):
    def test_legacy_frp_config_is_guarded(self) -> None:
        text = Path('scripts/install-server.sh').read_text(encoding='utf-8')
        guard = 'if [[ -s /etc/frp/frps.toml ]]; then'
        read = 'old_token="$(sed -n '
        guard_index = text.index(guard)
        read_index = text.index(read, guard_index)
        self.assertLess(guard_index, read_index)
        self.assertIn('old_token=""', text[max(0, guard_index - 80):guard_index])
        self.assertIn('fi', text[read_index:read_index + 500])


if __name__ == '__main__':
    unittest.main()
