# Эксплуатация

## Службы сервера

```bash
sudo systemctl status frps.service hermes-rdp.service
sudo journalctl -u frps.service -n 100 --no-pager
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

## CLI

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo hermes-rdpctl pair create --name 'Новый ПК'
sudo hermes-rdpctl devices rename DEVICE_ID 'Новое имя'
sudo hermes-rdpctl devices delete DEVICE_ID
sudo hermes-rdpctl dashboard reset
```

`dashboard reset` используется после ручного удаления сообщения Telegram. Затем отправь `/start`.

## Резервные копии

Серверный установщик хранит предыдущие файлы в `/var/backups/hermes-rdp`.

Windows-клиент сохраняет прежние файлы в `C:\ProgramData\HermesRDPackups`.
