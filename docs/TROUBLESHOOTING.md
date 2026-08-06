# Диагностика

## Сервер

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
sudo journalctl -u hermes-rdp-sshd.service -n 100 --no-pager
sudo /usr/sbin/sshd -t -f /etc/hermes-rdp/sshd_config
```

## Windows

```powershell
Get-WindowsCapability -Online -Name 'OpenSSH.Client*'
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Process ssh -ErrorAction SilentlyContinue
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
Get-Content 'C:\ProgramData\HermesRDP\ssh-error.log' -Tail 50
```

`REMOTE HOST IDENTIFICATION HAS CHANGED` означает несовпадение закреплённого SSH host key. Не удаляй `known_hosts` вслепую: сначала проверь, менялся ли серверный ключ.

`remote port forwarding failed` обычно означает занятый порт, отключённый ключ или несовпадение `permitlisten`.
