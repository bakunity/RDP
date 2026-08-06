# Тестирование Hermes RDP v1.1.0 от А до Я

## 1. Сервер

```bash
sudo hermes-rdpctl doctor
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
sudo /usr/sbin/sshd -t -f /etc/hermes-rdp/sshd_config
```

Ожидается: API `1.1.0`, tunnel `openssh`, порты `7000` и `7443` слушаются.

## 2. Внешняя сеть

```powershell
Test-NetConnection SERVER -Port 7000
Test-NetConnection SERVER -Port 7443
```

До установки клиента первый RDP-порт должен быть закрыт.

## 3. Pairing

Создай код в Telegram и выполни команду в PowerShell администратора. Не публикуй pairing-код, private key или fingerprint.

## 4. Windows после установки

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Process ssh -ErrorAction SilentlyContinue
Get-Service TermService
Get-NetTCPConnection -LocalPort 3389 -State Listen
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

## 5. RDP

```powershell
Test-NetConnection SERVER -Port 53389
mstsc.exe /v:SERVER:53389
```

## 6. Telegram

Проверь ONLINE, телеметрию, OFF, ON, RESTART и DELETE. OFF должен закрыть внешний порт, ON — восстановить. DELETE должен отозвать ключ и освободить порт.

## 7. Несколько устройств

Добавь второй ПК. Он должен получить другой порт и отдельный SSH key. Отключение первого ПК не должно влиять на второй.

## 8. Перезагрузки

Перезагрузи Windows и сервер. Scheduled Task и systemd должны восстановить туннели автоматически.

## 9. Security regression

- неверный API fingerprint отклоняется;
- неверный SSH host key отклоняется;
- ключ одного устройства не может открыть порт другого;
- удалённый ключ не авторизуется;
- Windows-установщик не скачивает FRP и не добавляет Defender exclusions.
