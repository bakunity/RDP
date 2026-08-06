# Эксплуатация Hermes RDP

## Быстрая проверка состояния

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
sudo ss -ltnp | grep -E ':(7000|7443|5338[9]|5339[0-9])\b'
```

## Логи сервера

```bash
sudo journalctl -u hermes-rdp-sshd.service -n 100 --no-pager
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

Логи могут содержать адреса и идентификаторы. Перед публикацией удаляйте pairing-коды, tokens, fingerprints и реальные IP/Telegram IDs.

## Перезапуск

```bash
sudo systemctl restart hermes-rdp-sshd.service hermes-rdp.service
```

После перезапуска Windows-агенты должны переподключиться автоматически.

## Backup

Сохраняйте:

- `/etc/hermes-rdp`;
- `/var/lib/hermes-rdp/state.sqlite3`;
- systemd units;
- текущий repository ref.

```bash
sudo tar -C / -czf /var/backups/hermes-rdp/manual-$(date -u +%Y%m%dT%H%M%SZ).tar.gz \
  etc/hermes-rdp \
  var/lib/hermes-rdp \
  etc/systemd/system/hermes-rdp.service \
  etc/systemd/system/hermes-rdp-sshd.service
```

Проверьте, что архив создан и не пуст:

```bash
sudo ls -lh /var/backups/hermes-rdp/manual-*.tar.gz | tail
```

## Обновление

1. Прочитайте release notes.
2. Создайте backup.
3. Используйте фиксированный release tag или проверенный commit.
4. Запустите `scripts/update-server.sh`.
5. Выполните `hermes-rdpctl doctor`.
6. Проверьте существующий Windows endpoint из внешней сети.

Не обновляйте production прямо с изменяемого `main`.

## Отзыв устройства

Удаление в Telegram:

- отзывает API-token;
- отзывает SSH public key;
- закрывает listener;
- освобождает порт.

После удаления проверьте:

```bash
sudo ss -H -ltn 'sport = :53389'
```

Вывод должен быть пустым.

## После перезагрузки сервера

```bash
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
sudo hermes-rdpctl doctor
```

Оба systemd service должны стартовать автоматически. Windows-агенты должны восстановить свои listeners после reconnect.

## После перезагрузки Windows

Scheduled Task запускается от `SYSTEM` с задержкой. В течение 30–90 секунд ожидаются:

- процесс `ssh.exe`;
- новый heartbeat;
- ONLINE в Telegram;
- открытый назначенный порт на сервере.

## Ротация и очистка

- храните ограниченное число проверенных backups;
- не удаляйте последний рабочий backup до полного acceptance PASS;
- legacy-каталоги Windows удаляйте только после проверки новой установки;
- не оставляйте отозванные устройства в registry без причины.
