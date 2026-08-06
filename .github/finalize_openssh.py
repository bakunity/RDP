from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f"missing patch anchor: {label}")


# Existing v1.0 databases do not have SSH columns yet. The index must be
# created only after ALTER TABLE adds those columns.
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
    raise SystemExit("SSH key index must be created exactly once after migration")
db_path.write_text(db, encoding="utf-8")


install_path = ROOT / "scripts/install-server.sh"
install = install_path.read_text(encoding="utf-8")
install = install.replace("Protocol 2\n", "", 1)
install = replace_once(
    install,
    '''CLOSED=0
while read -r PID; do
  [[ -n "$PID" && -r "/proc/$PID/cmdline" ]] || continue
  COMMAND="$(tr '\\0' ' ' < "/proc/$PID/cmdline")"
  if [[ "$COMMAND" == *"sshd: hermes-tunnel"* ]]; then
    kill -TERM "$PID"
    CLOSED=1
  fi
done < <(
''',
    '''CLOSED=0
while read -r PID; do
  [[ -n "$PID" && -e "/proc/$PID/exe" ]] || continue
  EXE="$(readlink -f "/proc/$PID/exe" 2>/dev/null || true)"
  if [[ "$EXE" == /usr/sbin/sshd ]]; then
    kill -TERM "$PID"
    CLOSED=1
  fi
done < <(
''',
    "close helper executable check",
)
install = replace_once(
    install,
    '''if ((MIGRATE == 1)); then
  rm -f /etc/systemd/system/frps.service /usr/local/bin/frps
fi
''',
    '''if ((MIGRATE == 1)); then
  rm -f /etc/systemd/system/frps.service /usr/local/bin/frps
  rm -rf /etc/frp
fi
''',
    "legacy FRP cleanup",
)
install = replace_once(
    install,
    '''systemctl daemon-reload
systemctl enable hermes-rdp-sshd.service hermes-rdp.service
systemctl restart hermes-rdp-sshd.service hermes-rdp.service
sleep 3

PYTHONPATH=/opt/hermes-rdp/app \\
  python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp
''',
    '''PYTHONPATH=/opt/hermes-rdp/app \\
  python3 -m compileall -q /opt/hermes-rdp/app/hermes_rdp

systemctl daemon-reload
systemctl enable hermes-rdp-sshd.service hermes-rdp.service
systemctl restart hermes-rdp-sshd.service hermes-rdp.service
sleep 3
''',
    "validation before service restart",
)
install_path.write_text(install, encoding="utf-8")


client_path = ROOT / "scripts/install-client.ps1"
client = client_path.read_text(encoding="utf-8-sig")
client = replace_once(
    client,
    '''    & $KeygenPath `
        -q `
        -t ed25519 `
        -N '' `
        -C "hermes-rdp-$env:COMPUTERNAME" `
        -f $SshKeyPath
    if ($LASTEXITCODE -ne 0) {
        throw "ssh-keygen завершился с кодом $LASTEXITCODE"
    }
''',
    '''    $KeygenProcess = Start-Process `
        -FilePath $KeygenPath `
        -ArgumentList @(
            '-q'
            '-t'
            'ed25519'
            '-N'
            '\"\"'
            '-C'
            "hermes-rdp-$env:COMPUTERNAME"
            '-f'
            $SshKeyPath
        ) `
        -Wait `
        -NoNewWindow `
        -PassThru
    if ($KeygenProcess.ExitCode -ne 0) {
        throw "ssh-keygen завершился с кодом $($KeygenProcess.ExitCode)"
    }
''',
    "PowerShell 5.1 empty passphrase forwarding",
)
client_path.write_text(client, encoding="utf-8-sig")
