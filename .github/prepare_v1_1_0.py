from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f"missing patch anchor: {label}")


bot_path = ROOT / "server/hermes_rdp/bot.py"
bot = bot_path.read_text(encoding="utf-8")
bot = replace_once(
    bot,
    "from .db import Registry\n",
    "from .db import Registry\nfrom .tunnel import close_tunnel\n",
    "bot tunnel import",
)
bot = replace_once(
    bot,
    '''        if data.startswith("cmd:"):
            _, action, device_id = data.split(":", 2)
            try:
                self.registry.queue_command(device_id, action)
                self._answer(callback_id, f"Команда {action.upper()} отправлена")
            except Exception as exc:
                self._answer(callback_id, str(exc))
            self.render()
            return
''',
    '''        if data.startswith("cmd:"):
            _, action, device_id = data.split(":", 2)
            try:
                device = self.registry.get_device(device_id)
                self.registry.set_enabled(device_id, action != "off")
                self.registry.queue_command(device_id, action)
                if action == "off":
                    try:
                        close_tunnel(self.config, int(device["rdp_port"]))
                    except Exception as exc:
                        LOG.warning("tunnel close failed: %s", exc)
                self._answer(callback_id, f"Команда {action.upper()} отправлена")
            except Exception as exc:
                self._answer(callback_id, str(exc))
            self.render()
            return
''',
    "bot command handler",
)
bot = replace_once(
    bot,
    '''        if data.startswith("delete_yes:"):
            device_id = data.split(":", 1)[1]
            self.registry.revoke_device(device_id)
            self.registry.set_setting("screen", "home")
            self.registry.set_setting("selected_device", "")
            self._answer(callback_id, "Устройство удалено")
            self.render()
            return
''',
    '''        if data.startswith("delete_yes:"):
            device_id = data.split(":", 1)[1]
            try:
                device = self.registry.get_device(device_id)
                self.registry.revoke_device(device_id)
                try:
                    close_tunnel(self.config, int(device["rdp_port"]))
                except Exception as exc:
                    LOG.warning("deleted tunnel close failed: %s", exc)
                self._answer(callback_id, "Устройство удалено")
            except Exception as exc:
                self._answer(callback_id, str(exc))
            self.registry.set_setting("screen", "home")
            self.registry.set_setting("selected_device", "")
            self.render()
            return
''',
    "bot delete handler",
)
bot = replace_once(
    bot,
    '            f"FRP-сервер: постоянно включён\\n"\n',
    '            f"OpenSSH-туннели: порт {self.config.ssh_bind_port}\\n"\n',
    "bot home transport",
)
bot = replace_once(
    bot,
    '            f"  Fingerprint=\'{self.config.tls_fingerprint}\'\\n"\n'
    '            "}\\n"\n',
    '            f"  Fingerprint=\'{self.config.tls_fingerprint}\'\\n"\n'
    '            f"  RepositoryRef=\'{self.config.repository_ref}\'\\n"\n'
    '            "}\\n"\n',
    "bot repository ref",
)
bot = replace_once(
    bot,
    '        frpc = telemetry.get("frpc_running", False)\n',
    '        ssh_tunnel = telemetry.get("ssh_tunnel_running", False)\n',
    "bot telemetry variable",
)
bot = replace_once(
    bot,
    '            f"FRPC: {\'работает\' if frpc else \'остановлен\'}\\n"\n',
    '            f"SSH-туннель: {\'работает\' if ssh_tunnel else \'остановлен\'}\\n"\n',
    "bot tunnel status",
)
bot = replace_once(
    bot,
    '            "Доступ к API будет отозван. Локальный клиент нужно удалить отдельным "\n'
    '            "скриптом на самом Windows-ПК."\n',
    '            "API-token и SSH-ключ будут отозваны, а RDP-порт освобождён. "\n'
    '            "Локальный клиент нужно удалить отдельным скриптом на Windows-ПК."\n',
    "bot delete warning",
)
bot_path.write_text(bot, encoding="utf-8")

version = "1.1.0"
(ROOT / "VERSION").write_text(version + "\n", encoding="utf-8")
(ROOT / "server/hermes_rdp/__init__.py").write_text(
    f'__version__ = "{version}"\n',
    encoding="utf-8",
)

pyproject_path = ROOT / "server/pyproject.toml"
pyproject = pyproject_path.read_text(encoding="utf-8")
pyproject, count = re.subn(
    r'(?m)^version\s*=\s*"[^"]+"$',
    f'version = "{version}"',
    pyproject,
    count=1,
)
if count != 1:
    raise SystemExit("unable to update pyproject version")
pyproject_path.write_text(pyproject, encoding="utf-8")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
old_head = '''## [Unreleased]

Пока нет изменений после `v1.0.7`.

## [1.0.7] — 2026-08-06
'''
new_head = '''## [Unreleased]

Пока нет изменений после `v1.1.0`.

## [1.1.0] — 2026-08-06

Крупный релиз: транспорт Hermes RDP переведён с FRP на системный OpenSSH.

### Добавлено

- отдельный изолированный `sshd` на порту `7000/tcp`;
- индивидуальный Ed25519-ключ и постоянный RDP-порт для каждого ПК;
- динамический `AuthorizedKeysCommand` с `permitlisten` только на назначенный порт;
- закрепление SSH host key через уже закреплённый HTTPS API;
- автоматическое восстановление reverse SSH-туннеля после обрыва или перезагрузки;
- атомарный pairing, отзыв SSH-ключа и повторное использование освобождённых портов.

### Изменено

- Windows использует встроенные `ssh.exe` и `ssh-keygen.exe`;
- Telegram ON/OFF/RESTART управляет OpenSSH-туннелем;
- OFF и DELETE закрывают активный listener на сервере;
- миграция с `v1.0.x` выполняется явно через `--migrate`.

### Удалено

- `frps`, `frpc.exe`, загрузка стороннего FRP-архива и Defender exclusions.

### Безопасность

- tunnel-user не получает shell, PTY, SFTP, agent forwarding или произвольные порты;
- private key остаётся только на Windows-ПК;
- удаление устройства отзывает API-token и SSH public key.

## [1.0.7] — 2026-08-06
'''
changelog = replace_once(changelog, old_head, new_head, "changelog head")
changelog = replace_once(
    changelog,
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.7...HEAD",
    "[Unreleased]: https://github.com/bakunity/RDP/compare/v1.1.0...HEAD\n"
    "[1.1.0]: https://github.com/bakunity/RDP/releases/tag/v1.1.0",
    "changelog links",
)
changelog_path.write_text(changelog, encoding="utf-8")

# Existing SQLite databases must add columns before creating the new index.
db_path = ROOT / "server/hermes_rdp/db.py"
db = db_path.read_text(encoding="utf-8")
schema_index = '''
CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_active_ssh_key
ON devices(ssh_public_key)
WHERE revoked=0 AND ssh_public_key IS NOT NULL AND ssh_public_key<>'';
'''
if schema_index in db:
    db = db.replace(schema_index, "", 1)
if db.count("CREATE UNIQUE INDEX IF NOT EXISTS idx_devices_active_ssh_key") != 1:
    raise SystemExit("SSH key index must only be created after column migration")
db_path.write_text(db, encoding="utf-8")

install_path = ROOT / "scripts/install-server.sh"
install = install_path.read_text(encoding="utf-8")
install = install.replace("Protocol 2\n", "", 1)
old_order = '''systemctl daemon-reload
systemctl enable hermes-rdp-sshd.service hermes-rdp.service
systemctl restart hermes-rdp-sshd.service hermes-rdp.service
sleep 3

PYTHONPATH=/opt/hermes-rdp/app \\
  python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp
'''
new_order = '''PYTHONPATH=/opt/hermes-rdp/app \\
  python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp

systemctl daemon-reload
systemctl enable hermes-rdp-sshd.service hermes-rdp.service
systemctl restart hermes-rdp-sshd.service hermes-rdp.service
sleep 3
'''
install = replace_once(install, old_order, new_order, "installer validation order")
install_path.write_text(install, encoding="utf-8")
