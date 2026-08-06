# Шпаргалка команд

## Hermes: status

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo systemctl status frps.service hermes-rdp.service --no-pager
```

```bash
sudo hermes-rdpctl devices list
```

## Hermes: pairing

Автоматический порт:

```bash
sudo hermes-rdpctl pair create --name 'Ноутбук'
```

Конкретный порт:

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-01' --port 53389
```

TTL 5 минут:

```bash
sudo hermes-rdpctl pair create --name 'Ноутбук' --ttl 300
```

## Hermes: устройства

```bash
sudo hermes-rdpctl devices rename DEVICE_ID 'Новое имя'
```

```bash
sudo hermes-rdpctl devices delete DEVICE_ID
```

## Hermes: dashboard

```bash
sudo hermes-rdpctl dashboard reset
sudo systemctl restart hermes-rdp.service
```

Затем `/start` в Telegram.

## Hermes: logs

```bash
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

```bash
sudo journalctl -u frps.service -n 100 --no-pager
```

```bash
sudo journalctl -u hermes-rdp.service -f
```

## Hermes: ports

```bash
sudo ss -lntp | grep -E ':(7000|7443|53389)\b'
```

```bash
sudo ufw status numbered
```

## Windows: agent

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
```

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 100
```

```powershell
Stop-ScheduledTask -TaskName 'Hermes RDP Agent' -ErrorAction SilentlyContinue; Start-ScheduledTask -TaskName 'Hermes RDP Agent'
```

## Windows: FRPC

```powershell
Get-Process frpc -ErrorAction SilentlyContinue
```

```powershell
& 'C:\ProgramData\HermesRDP\frpc.exe' verify -c 'C:\ProgramData\HermesRDP\frpc.toml'
```

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 7000
```

## Windows: RDP

```powershell
Get-Service TermService
```

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

## Stable install v1.0.7

Server:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
```

Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/install-client.ps1'; & ([scriptblock]::Create((irm $u))) -Server 'SERVER' -PairCode 'CODE' -Fingerprint 'FINGERPRINT' -Name 'PC NAME' -RepositoryRef 'v1.0.7'
```

## Stable update v1.0.7

Server:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/update-server.sh -o /tmp/update-hermes-rdp.sh
sudo env HERMES_RDP_REF=v1.0.7 bash /tmp/update-hermes-rdp.sh
rm -f /tmp/update-hermes-rdp.sh
```

Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/update-client.ps1'; & ([scriptblock]::Create((irm $u))) -RepositoryRef 'v1.0.7'
```

## Uninstall

Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/uninstall-client.ps1'; & ([scriptblock]::Create((irm $u)))
```

Server, только после backup:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.0.7/scripts/uninstall-server.sh -o /tmp/uninstall-hermes-rdp.sh
sudo bash /tmp/uninstall-hermes-rdp.sh
```

## Release links

```text
Latest: https://github.com/bakunity/RDP/releases/latest
v1.0.7: https://github.com/bakunity/RDP/releases/tag/v1.0.7
```
