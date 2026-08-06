from __future__ import annotations

from pathlib import Path


root = Path(__file__).resolve().parents[1]
old_version = "1.0.4"
new_version = "1.0.5"

bot_path = root / "server/hermes_rdp/bot.py"
bot = bot_path.read_text(encoding="utf-8")
old_command = '''        command = (
            "$u='" + self.config.client_installer_url + "'; "
            "& ([scriptblock]::Create((irm $u))) "
            f"-Server '{self.config.public_host}' "
            f"-PairCode '{code}' "
            f"-Fingerprint '{self.config.tls_fingerprint}'"
        )
'''
new_command = '''        command = (
            "$u='" + self.config.client_installer_url + "'\\n"
            "$p=@{\\n"
            f"  Server='{self.config.public_host}'\\n"
            f"  PairCode='{code}'\\n"
            f"  Fingerprint='{self.config.tls_fingerprint}'\\n"
            "}\\n"
            "& ([scriptblock]::Create((irm $u))) @p"
        )
'''
if old_command not in bot:
    raise SystemExit("single-line Telegram command anchor missing")
bot_path.write_text(bot.replace(old_command, new_command, 1), encoding="utf-8")

installer_path = root / "scripts/install-server.sh"
installer = installer_path.read_text(encoding="utf-8")
old_service_start = "systemctl enable --now frps.service hermes-rdp.service\n"
new_service_start = (
    "systemctl enable frps.service hermes-rdp.service\n"
    "systemctl restart frps.service hermes-rdp.service\n"
)
if old_service_start not in installer:
    raise SystemExit("install-server systemd anchor missing")
installer_path.write_text(
    installer.replace(old_service_start, new_service_start, 1),
    encoding="utf-8",
)

updater_path = root / "scripts/update-server.sh"
updater = updater_path.read_text(encoding="utf-8")
old_archive = "https://github.com/$REPO/archive/refs/heads/$REF.tar.gz"
new_archive = "https://codeload.github.com/$REPO/tar.gz/$REF"
if old_archive not in updater:
    raise SystemExit("update-server archive anchor missing")
updater_path.write_text(updater.replace(old_archive, new_archive, 1), encoding="utf-8")

pair_test = r'''from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hermes_rdp.bot import TelegramBot
from hermes_rdp.config import Config


class FakeRegistry:
    def __init__(self) -> None:
        self.settings = {
            "screen": "pair",
            "pair_code": "ABCD1234",
            "dashboard_message_id": "",
        }

    def get_setting(self, key: str, default: str = "") -> str:
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: str) -> None:
        self.settings[key] = value


class TelegramPairCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        token = root / "telegram-token"
        fingerprint = root / "api.sha256"
        frp_token = root / "frp-token"
        token.write_text("test-token", encoding="utf-8")
        fingerprint.write_text("AA11BB22", encoding="utf-8")
        frp_token.write_text("frp-token", encoding="utf-8")
        self.registry = FakeRegistry()
        self.config = Config(
            public_host="server.example",
            api_port=7443,
            frp_bind_port=7000,
            port_start=53389,
            port_end=53420,
            data_dir=root,
            db_path=root / "state.sqlite3",
            telegram_token_file=token,
            telegram_chat_id="123",
            tls_cert_file=root / "api.crt",
            tls_key_file=root / "api.key",
            tls_fingerprint_file=fingerprint,
            frp_token_file=frp_token,
            frp_ca_file=root / "frp-ca.crt",
            client_installer_url="https://example.test/install-client.ps1?a=1&b=2",
        )
        self.bot = TelegramBot(self.config, self.registry)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_pair_command_is_one_compact_multiline_code_block(self) -> None:
        text, _ = self.bot._pair()
        self.assertEqual(text.count("<pre><code>"), 1)
        self.assertEqual(text.count("</code></pre>"), 1)
        self.assertIn("$p=@{\n", text)
        self.assertIn("Server=&#x27;server.example&#x27;", text)
        self.assertIn("PairCode=&#x27;ABCD1234&#x27;", text)
        self.assertIn("Fingerprint=&#x27;AA11BB22&#x27;", text)
        self.assertIn("a=1&amp;b=2", text)
        self.assertIn("@p</code></pre>", text)
        self.assertNotIn("`", text)
        code = text.split("<pre><code>", 1)[1].split("</code></pre>", 1)[0]
        self.assertLess(max(map(len, code.splitlines())), 100)

    def test_render_requests_html_parse_mode(self) -> None:
        calls = []

        def fake_api_call(method, payload=None, timeout=40):
            calls.append((method, payload, timeout))
            return {"message_id": 77}

        self.bot.api_call = fake_api_call
        self.bot.render()
        method, payload, _ = calls[-1]
        self.assertEqual(method, "sendMessage")
        self.assertEqual(payload["parse_mode"], "HTML")
        self.assertIn("<pre><code>", payload["text"])


if __name__ == "__main__":
    unittest.main()
'''
(root / "tests/test_bot_pair_copy.py").write_text(pair_test, encoding="utf-8")

restart_test = r'''from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ServerUpdateBehaviorTests(unittest.TestCase):
    def test_install_server_restarts_active_services(self) -> None:
        text = (ROOT / "scripts/install-server.sh").read_text(encoding="utf-8")
        self.assertIn("systemctl enable frps.service hermes-rdp.service", text)
        self.assertIn("systemctl restart frps.service hermes-rdp.service", text)
        self.assertNotIn("systemctl enable --now frps.service hermes-rdp.service", text)

    def test_update_server_accepts_branch_or_tag_ref(self) -> None:
        text = (ROOT / "scripts/update-server.sh").read_text(encoding="utf-8")
        self.assertIn("https://codeload.github.com/$REPO/tar.gz/$REF", text)
        self.assertNotIn("archive/refs/heads/$REF.tar.gz", text)
        self.assertIn("systemctl restart hermes-rdp.service", text)


if __name__ == "__main__":
    unittest.main()
'''
(root / "tests/test_server_update_behavior.py").write_text(restart_test, encoding="utf-8")

excluded = {
    Path("CHANGELOG.md"),
    Path("docs/releases/v1.0.0.md"),
    Path("docs/releases/v1.0.1.md"),
    Path("docs/releases/v1.0.2.md"),
    Path("docs/releases/v1.0.3.md"),
    Path("docs/releases/v1.0.4.md"),
    Path(".github/workflows/prepare-v1-0-5.yml"),
    Path("scripts/prepare_v1_0_5.py"),
}
allowed = {".md", ".py", ".toml", ".html", ".xml", ".txt", ".json", ".sh", ".js", ".css"}
for path in root.rglob("*"):
    relative = path.relative_to(root)
    if not path.is_file() or ".git" in path.parts or relative in excluded:
        continue
    if path.name != "VERSION" and path.suffix.lower() not in allowed:
        continue
    data = path.read_text(encoding="utf-8")
    updated = data.replace("v" + old_version, "v" + new_version).replace(old_version, new_version)
    if updated != data:
        path.write_text(updated, encoding="utf-8")

(root / "VERSION").write_text(new_version + "\n", encoding="utf-8")

changelog_path = root / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
marker = "## [1.0.4] — 2026-08-06\n"
section = '''## [1.0.5] — 2026-08-06

UX-патч компактной команды Telegram и исправление обновления активного сервиса.

### Изменено

- команда Windows-установщика остаётся одним копируемым блоком, но разбита на короткие строки через PowerShell splatting;
- убрана чрезмерная ширина Telegram code block;
- команда не использует хрупкие символы продолжения строки PowerShell;
- повторный запуск серверного установщика явно перезапускает уже активные `frps` и `hermes-rdp`;
- `update-server.sh` корректно загружает как ветки, так и release-теги;
- добавлены regression tests Telegram-разметки и поведения обновления.

### Совместимость

- pairing contract, API, SQLite, FRP-протокол и Windows agent не изменены;
- стандартные порты не изменены.

'''
if marker not in changelog:
    raise SystemExit("CHANGELOG insertion marker missing")
changelog = changelog.replace("Пока нет изменений после `v1.0.4`.", "Пока нет изменений после `v1.0.5`.")
changelog = changelog.replace(marker, section + marker, 1)
changelog = changelog.replace(
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.4...HEAD",
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.5...HEAD",
)
changelog = changelog.replace(
    "[1.0.4]: https://github.com/bakunity/RDP/releases/tag/v1.0.4",
    "[1.0.5]: https://github.com/bakunity/RDP/releases/tag/v1.0.5\n"
    "[1.0.4]: https://github.com/bakunity/RDP/releases/tag/v1.0.4",
)
changelog_path.write_text(changelog, encoding="utf-8")

notes = '''# Hermes RDP v1.0.5

UX-патч Telegram-команды и серверного обновления.

## Изменено

PowerShell-команда добавления Windows-ПК остаётся единым копируемым блоком, но теперь использует несколько коротких строк и splatting. Telegram больше не растягивает панель из-за одной длинной строки, а команда не зависит от хрупких обратных апострофов.

Серверный установщик теперь явно перезапускает уже работающие службы после обновления. `update-server.sh` загружает исходники через endpoint, совместимый и с ветками, и с release-тегами.

## Совместимость

- API, SQLite registry, pairing contract, FRP и Windows agent не изменены;
- стандартные порты не изменены.

## Ссылки

- [GitHub Release v1.0.5](https://github.com/bakunity/RDP/releases/tag/v1.0.5)
- [Тестирование от А до Я](https://github.com/bakunity/RDP/blob/v1.0.5/docs/TESTING_A_TO_Z.md)
'''
(root / "docs/releases/v1.0.5.md").write_text(notes, encoding="utf-8")

(root / ".github/workflows/prepare-v1-0-5.yml").unlink()
Path(__file__).unlink()
