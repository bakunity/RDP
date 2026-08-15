# Установка сервера

## Поддерживаемая среда

Debian/Ubuntu, root или sudo, systemd, публичный IPv4 и доступ к GitHub/Telegram API.

## Порты

- `22/tcp` — административный SSH сервера, Hermes его не меняет;
- `7000/tcp` — отдельный Hermes OpenSSH daemon;
- `7443/tcp` — HTTPS API;
- `53389–53420/tcp` — RDP endpoints;
- `80/tcp` — используется автоматически для trusted RDP certificate lifecycle через ACME HTTP-01.

## Рекомендуемая установка

Для обычного нового сервера используйте одну команду:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install.sh | sudo bash
```

Zero-config bootstrap предназначен для интерактивной установки человеком. Он сам выполняет preflight, определяет public IPv4, привязывает владельца Telegram и запускает основной Hermes installer.

### Что происходит по шагам

1. Проверяется Debian/Ubuntu, root и systemd.
2. Выполняется `apt-get update` до установки Hermes.
3. Для известного stale Debian source на `archive.debian.org` bootstrap может выполнить узкое автоматическое исправление только после проверки, что текущий codename опубликован на `deb.debian.org`; перед изменением source-файлы сохраняются в `/var/backups/hermes-rdp/apt-sources-*`.
4. Определяется глобальный public IPv4.
5. Bot token вводится скрыто через `/dev/tty` и проверяется Telegram `getMe`.
6. Installer проверяет, что бот не занят существующим webhook.
7. Генерируется одноразовый `/claim XXXXXXXX`.
8. Владелец отправляет claim-код боту в private chat. Installer принимает только сообщение, где `chat.id == from.id`, после чего использует этот Telegram ID как постоянный owner ID Hermes.
9. Запускается основной `install-server.sh` с уже определённым host и подтверждённым owner ID.
10. После успешного core install автоматически запускается trusted RDP certificate setup.

Bot token не выводится в терминал. Claim code существует только во время bootstrap-run и не становится постоянным credential.

## APT preflight

Hermes не должен начинать собственное развёртывание на системе с нерабочим package manager.

Если `apt-get update` падает, installer сначала показывает понятную диагностику. Известный случай:

```text
E: The repository 'http://archive.debian.org/debian trixie Release' does not have a Release file.
```

обрабатывается специально: если текущий Debian codename доступен на официальном live mirror, bootstrap делает backup соответствующих source-файлов, заменяет только stale `archive.debian.org` URL на актуальные Debian endpoints и снова проверяет APT.

Если повторная проверка не проходит, source-файлы восстанавливаются. Hermes при этом ещё не устанавливается.

## Telegram owner claim

Числовой Telegram ID больше не требуется заранее искать и вручную подставлять в основную пользовательскую команду.

После проверки bot token терминал покажет, например:

```text
Привязка владельца Telegram
1. Откройте @my_hermes_bot в Telegram.
2. Отправьте боту ровно эту команду:

   /claim 12345678
```

Bootstrap ждёт подтверждение ограниченное время. Первый случайный `/start` **не** становится владельцем. Нужен именно неизвестный заранее одноразовый claim code, показанный только в терминале сервера.

После успешного claim в постоянный Hermes config записывается уже подтверждённый Telegram owner ID, поэтому штатная authorization model Telegram controller не ослабляется.

## Trusted RDP certificate — automatic

Обычному пользователю не нужно выбирать «установка с сертификатом» или «без сертификата».

После успешного core install bootstrap автоматически пытается включить публично доверенный сертификат **Windows RDP listener** для обнаруженного public IPv4.

Если ACME доступен:

```text
Trusted RDP TLS: active
```

Hermes устанавливает Certbot lifecycle, renewal timer, non-secret certificate state и authenticated Windows delivery path.

Если TCP `80` занят, недоступен извне или ACME временно не проходит, setup сертификата может завершиться ошибкой, но **core Hermes уже установлен и остаётся рабочим**:

```text
Trusted RDP TLS: unavailable
```

После исправления сети certificate lifecycle можно включить отдельно. HTTPS API certificate pinning не зависит от этого и остаётся отдельной trust boundary.

## Advanced / automation interface

`scripts/install-server.sh` сохраняется как низкоуровневый интерфейс для CI, кастомного DNS/NAT, нестандартных портов, migration и полностью scripted deployments:

```bash
scripts/install-server.sh \
  --host HOST \
  --telegram-token TOKEN \
  --telegram-chat-id TELEGRAM_USER_ID \
  --api-port 7443 \
  --ssh-port 7000 \
  --port-start 53389 \
  --port-end 53420
```

Строгий `--trusted-rdp-cert` также остаётся доступен здесь. В advanced mode failure certificate setup считается failure всей команды, что удобно для automation, где trusted TLS является обязательным контрактом.

## Что создаётся

Core Hermes:

- `/opt/hermes-rdp/app`;
- `/etc/hermes-rdp/config.json`;
- `/etc/hermes-rdp/tls/`;
- отдельный SSH host key;
- `/var/lib/hermes-rdp/state.sqlite3`;
- `hermes-rdp.service`;
- `hermes-rdp-sshd.service`;
- системные пользователи `hermes-rdp` и `hermes-tunnel`.

При успешном automatic trusted TLS дополнительно создаются Hermes certificate helpers/state и systemd renewal service/timer.

## Проверка

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
sudo /usr/sbin/sshd -t -f /etc/hermes-rdp/sshd_config
sudo ss -ltnp | grep -E ':(7000|7443)\b'
```

Ожидается:

```text
config: OK
api: OK (..., openssh)
ssh-tunnel: LISTEN 7000
api: LISTEN 7443
ssh-config: OK
```

При active trusted lifecycle:

```bash
sudo systemctl is-enabled hermes-rdp-cert-renew.timer
sudo systemctl is-active hermes-rdp-cert-renew.timer
sudo cat /etc/hermes-rdp/trusted-rdp-cert-state.json
```

До подключения первого ПК RDP-порты должны быть закрыты. Порт появляется только после успешного reverse-туннеля.

## Backup

Основной server installer создаёт backup в `/var/backups/hermes-rdp/`. APT source auto-repair, если понадобился, хранит отдельный backup в `/var/backups/hermes-rdp/apt-sources-*`.

Не удаляйте backup до прохождения внешнего RDP-теста.

## После установки

1. Отправьте `/start` Telegram-боту.
2. Добавьте первый Windows-ПК через **➕ ДОБАВИТЬ ПК**.
3. Вставьте выданную ботом PowerShell-команду на Windows.
4. Проверьте endpoint из другой сети стандартным Microsoft Remote Desktop.
5. Если `Trusted RDP TLS: active`, Microsoft Remote Desktop должен принимать listener certificate без прежнего self-signed warning.
