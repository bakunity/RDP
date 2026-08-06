from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[1]
old_version = "1.0.5"
new_version = "1.0.6"

bot_path = root / "server/hermes_rdp/bot.py"
bot = bot_path.read_text(encoding="utf-8")
old_command = '''        command = (
            "$u='" + self.config.client_installer_url + "'\\n"
            "$p=@{\\n"
            f"  Server='{self.config.public_host}'\\n"
            f"  PairCode='{code}'\\n"
            f"  Fingerprint='{self.config.tls_fingerprint}'\\n"
            "}\\n"
            "& ([scriptblock]::Create((irm $u))) @p"
        )
'''
new_command = '''        command = (
            "$u='" + self.config.client_installer_url + "'\\n"
            "$s=(irm $u).TrimStart([char]0xFEFF)\\n"
            "$p=@{\\n"
            f"  Server='{self.config.public_host}'\\n"
            f"  PairCode='{code}'\\n"
            f"  Fingerprint='{self.config.tls_fingerprint}'\\n"
            "}\\n"
            "& ([scriptblock]::Create($s)) @p"
        )
'''
if old_command not in bot:
    raise SystemExit("Telegram bootstrap anchor missing")
bot_path.write_text(bot.replace(old_command, new_command, 1), encoding="utf-8")

test_path = root / "tests/test_bot_pair_copy.py"
test = test_path.read_text(encoding="utf-8")
old_assertions = '''        self.assertIn("$p=@{\\n", text)
        self.assertIn("Server=&#x27;server.example&#x27;", text)
'''
new_assertions = '''        self.assertIn("$s=(irm $u).TrimStart([char]0xFEFF)\\n", text)
        self.assertIn("$p=@{\\n", text)
        self.assertIn("Server=&#x27;server.example&#x27;", text)
'''
if old_assertions not in test:
    raise SystemExit("Telegram test anchor missing")
test = test.replace(old_assertions, new_assertions, 1)
test = test.replace(
    '        self.assertIn("@p</code></pre>", text)\n',
    '        self.assertIn("&amp; ([scriptblock]::Create($s)) @p</code></pre>", text)\n'
    '        self.assertNotIn("Create((irm $u))", text)\n',
    1,
)
test_path.write_text(test, encoding="utf-8")

excluded = {
    Path("CHANGELOG.md"),
    Path("docs/releases/v1.0.0.md"),
    Path("docs/releases/v1.0.1.md"),
    Path("docs/releases/v1.0.2.md"),
    Path("docs/releases/v1.0.3.md"),
    Path("docs/releases/v1.0.4.md"),
    Path("docs/releases/v1.0.5.md"),
    Path(".github/prepare_v1_0_6.py"),
    Path(".github/workflows/prepare-v1-0-6.yml"),
}
allowed = {".md", ".py", ".toml", ".html", ".xml", ".txt", ".json", ".sh", ".js", ".css", ".yml", ".yaml"}
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
marker = "## [1.0.5] — 2026-08-06\n"
section = '''## [1.0.6] — 2026-08-06

Hotfix запуска Windows-установщика через Telegram-команду в PowerShell 5.1.

### Исправлено

- перед `ScriptBlock.Create()` удаляется декодированный UTF-8 BOM (`U+FEFF`);
- начальный `param(...)` установщика снова корректно распознаётся при загрузке через `irm`;
- Telegram-команда остаётся компактной, многострочной и копируется одним нажатием;
- regression test проверяет наличие BOM-нормализации и запрещает возврат прямого `Create((irm $u))`.

### Совместимость

- сам `install-client.ps1` остаётся в UTF-8 BOM для корректной работы русского текста в Windows PowerShell 5.1;
- API, SQLite registry, pairing contract, FRP и стандартные порты не изменены.

'''
if marker not in changelog:
    raise SystemExit("CHANGELOG marker missing")
changelog = changelog.replace("Пока нет изменений после `v1.0.5`.", "Пока нет изменений после `v1.0.6`.")
changelog = changelog.replace(marker, section + marker, 1)
changelog = changelog.replace(
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.5...HEAD",
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.6...HEAD",
)
changelog = changelog.replace(
    "[1.0.5]: https://github.com/bakunity/RDP/releases/tag/v1.0.5",
    "[1.0.6]: https://github.com/bakunity/RDP/releases/tag/v1.0.6\n"
    "[1.0.5]: https://github.com/bakunity/RDP/releases/tag/v1.0.5",
)
changelog_path.write_text(changelog, encoding="utf-8")

notes = '''# Hermes RDP v1.0.6

Hotfix Telegram bootstrap для Windows PowerShell 5.1.

## Исправлено

При загрузке `install-client.ps1` через `Invoke-RestMethod` UTF-8 BOM мог сохраняться в строке как символ `U+FEFF`. Из-за этого `ScriptBlock.Create()` не распознавал начальный `param(...)` и выдавал ошибку на параметре `ApiPort`.

Telegram-команда теперь удаляет BOM перед созданием script block. Команда остаётся единым компактным копируемым блоком.

## Проверки

- regression tests проверяют наличие `TrimStart([char]0xFEFF)` и отсутствие старого прямого bootstrap;
- Windows PowerShell 5.1 CI продолжает разбирать все `.ps1` файлы;
- полный release check проходит на Linux.

## Совместимость

- API, SQLite registry, pairing contract, FRP и Windows agent не изменены;
- стандартные порты не изменены.

## Ссылки

- [GitHub Release v1.0.6](https://github.com/bakunity/RDP/releases/tag/v1.0.6)
- [Тестирование от А до Я](https://github.com/bakunity/RDP/blob/v1.0.6/docs/TESTING_A_TO_Z.md)
'''
(root / "docs/releases/v1.0.6.md").write_text(notes, encoding="utf-8")

(root / ".github/prepare_v1_0_6.py").unlink()
(root / ".github/workflows/prepare-v1-0-6.yml").unlink()
