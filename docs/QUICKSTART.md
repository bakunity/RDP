# Быстрый старт Hermes RDP

Этот путь рассчитан на чистый Debian/Ubuntu-сервер и Windows 10/11 Pro, Enterprise или Education.

Current stable release: **v1.3.0**. Новый zero-config bootstrap пока развивается в `main`; сам advanced installer и release tags остаются доступны для автоматизации и immutable deployments.

## 1. Что понадобится

- Linux-сервер Debian/Ubuntu с публичным IPv4;
- root/sudo и systemd;
- Telegram bot token;
- Windows x64 с правами администратора.

Windows Home не является штатным RDP-host и не поддерживается.

## 2. Установка сервера — основной путь

Одна команда:

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install.sh | sudo bash
```

Дальше installer сам:

1. определяет Debian/Ubuntu и проверяет systemd;
2. проверяет APT до изменений Hermes;
3. для известного случая со stale `archive.debian.org` на ещё поддерживаемом Debian делает узкое исправление с backup source-файлов и повторной проверкой;
4. определяет глобальный public IPv4;
5. просит ввести Telegram bot token без отображения его в терминале;
6. проверяет bot token через Telegram `getMe`;
7. показывает одноразовую команду `/claim XXXXXXXX`;
8. ждёт эту команду только из private chat и привязывает Telegram user/chat ID владельца;
9. устанавливает Hermes OpenSSH gateway, API и Telegram controller;
10. автоматически пытается включить trusted RDP certificate lifecycle.

Пример интерактивной части:

```text
=== HERMES RDP INSTALLER ===
✓ OS: Debian GNU/Linux
✓ APT repositories
✓ Public IPv4: 203.0.113.10

Telegram bot token:
✓ Telegram bot: @my_hermes_bot

Привязка владельца Telegram
Отправьте боту:

/claim 12345678

✓ Telegram owner confirmed
...
=== HERMES RDP READY ===
```

Claim code действует только в текущем запуске installer, не записывается в Hermes config и после подтверждения больше не нужен. Bot token не печатается в output.

### Trusted RDP TLS

Отдельную команду выбирать не нужно. После успешной установки core Hermes bootstrap сам запускает trusted public-IP certificate setup.

Если public-IP ACME доступен, получаем:

```text
Trusted RDP TLS: active
```

Если TCP `80` занят/закрыт внешним firewall или ACME временно недоступен, **основной Hermes остаётся установленным и рабочим**, а installer выдаёт предупреждение:

```text
Trusted RDP TLS: unavailable
```

HTTPS API certificate pinning при этом остаётся отдельной trust boundary и продолжает работать.

## 3. Если APT сломан

Installer выполняет APT preflight **до установки Hermes**. Вместо сырого падения посередине вы увидите понятную диагностику и последние строки `apt-get update`.

Для конкретного stale-сценария вида:

```text
http://archive.debian.org/debian trixie
```

bootstrap сначала проверит, что codename существует на актуальном Debian mirror, сохранит исходные source-файлы в `/var/backups/hermes-rdp/apt-sources-*`, заменит только известный stale archive URL и повторит `apt-get update`.

Если узкое автоматическое исправление не подходит или не помогает, исходные source-файлы восстанавливаются, Hermes не устанавливается, а пользователь исправляет APT вручную и запускает **ту же одну команду** повторно.

## 4. Advanced / automation installer

Для CI, нестандартного DNS/NAT, фиксированного immutable ref, явных портов и scripted deployments старый интерфейс остаётся доступен:

```bash
scripts/install-server.sh \
  --host HOST \
  --telegram-token TOKEN \
  --telegram-chat-id TELEGRAM_USER_ID
```

Именно advanced interface сохраняет явные `--host`, `--telegram-chat-id`, диапазон портов и строгий `--trusted-rdp-cert` режим. Zero-config bootstrap является удобным безопасным frontend поверх него.

Не публикуйте bot token, pairing-коды, API fingerprint, PFX material или приватные ключи.

## 5. Добавление ПК

1. Отправьте `/start` Telegram-боту.
2. Нажмите **➕ ДОБАВИТЬ ПК**.
3. Откройте PowerShell от имени администратора.
4. Вставьте готовую команду из Telegram целиком.
5. Введите понятное название компьютера.
6. Дождитесь `=== ГОТОВО ===`.

Установщик Windows создаёт локальный Ed25519-ключ, проверяет API certificate fingerprint и SSH host key, включает RDP и регистрирует `Hermes RDP Agent`.

Если trusted certificate lifecycle активен на сервере, Fresh Install автоматически создаёт `Hermes RDP Certificate Rotation` и применяет текущий trusted CUSTOM certificate. Отдельная ручная certificate setup-команда не нужна.

## 6. Подключение

```powershell
mstsc.exe /v:SERVER_IP:53389
```

Первый ПК обычно получает `53389`, следующий — `53390` и так далее.

Проверяйте подключение из другой сети, например через мобильный интернет телефона.

## 7. Проверка сервера

```bash
sudo hermes-rdpctl doctor
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
sudo ss -ltnp | grep -E ':(7000|7443)\b'
```

При активном trusted lifecycle:

```bash
sudo systemctl is-active hermes-rdp-cert-renew.timer
sudo cat /etc/hermes-rdp/trusted-rdp-cert-state.json
```

До подключения первого ПК RDP-порты должны быть закрыты.

## 8. Финальная проверка

- устройство отображается online в Telegram;
- `ssh.exe` работает на Windows;
- назначенный порт слушается на сервере;
- внешний RDP работает из другой сети;
- `Hermes RDP Agent` находится в Running;
- при trusted lifecycle `Hermes RDP Certificate Rotation` работает от LocalSystem, а RDP listener имеет CUSTOM certificate binding;
- Microsoft Defender остаётся включён и Hermes не требует exclusions;
- после перезагрузки Windows туннель восстанавливается автоматически;
- второй ПК получает отдельный порт и отдельный ключ.

Полная процедура: [TESTING_A_TO_Z.md](TESTING_A_TO_Z.md).
