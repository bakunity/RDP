# Эксплуатация

```bash
sudo hermes-rdpctl doctor
sudo hermes-rdpctl devices list
sudo journalctl -u hermes-rdp-sshd.service -u hermes-rdp.service -n 100 --no-pager
```

Перезапуск:

```bash
sudo systemctl restart hermes-rdp-sshd.service hermes-rdp.service
```

Обновление внутри ветки OpenSSH:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/v1.1.0/scripts/update-server.sh -o /tmp/update-hermes-rdp.sh
sudo env HERMES_RDP_REF=v1.1.0 bash /tmp/update-hermes-rdp.sh
```

Удаление устройства через Telegram выполняет жёсткий отзыв ключа и освобождает порт. OFF сохраняет устройство и порт, но запрещает SSH-авторизацию до ON.
