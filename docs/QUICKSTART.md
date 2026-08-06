# Быстрый старт Hermes RDP

Этот путь рассчитан на чистый Debian/Ubuntu-сервер и Windows 10/11 Pro, Enterprise или Education.

## 1. Что понадобится

- Linux-сервер с публичным IPv4 или доменом;
- root/sudo и systemd;
- свободные TCP-порты `7000`, `7443` и диапазон RDP;
- Telegram bot token и ваш числовой Telegram ID;
- Windows x64 с правами администратора.

Windows Home не является штатным RDP-host и не поддерживается.

## 2. Установка сервера

До появления официального release tag используйте проверенный source ref проекта, а не изменяемый `main`.

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/REF/scripts/install-server.sh -o /tmp/install-hermes-rdp.sh
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
sudo env HERMES_RDP_REF=REF bash /tmp/install-hermes-rdp.sh \
  --host SERVER_IP_OR_DOMAIN \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id TELEGRAM_USER_ID
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

Не публикуйте bot token, pairing-код, API fingerprint или приватные ключи.

## 3. Проверка сервера

```bash
sudo hermes-rdpctl doctor
sudo systemctl is-active hermes-rdp-sshd.service hermes-rdp.service
sudo ss -ltnp | grep -E ':(7000|7443)\b'
```

Ожидается `api: OK`, `ssh-tunnel: LISTEN 7000` и два активных сервиса.

До подключения первого ПК RDP-порты должны быть закрыты.

## 4. Добавление ПК

1. Отправьте `/start` Telegram-боту.
2. Нажмите **➕ ДОБАВИТЬ ПК**.
3. Откройте PowerShell от имени администратора.
4. Вставьте готовую команду из Telegram целиком.
5. Введите понятное название компьютера.
6. Дождитесь `=== ГОТОВО ===`.

Установщик создаёт локальный Ed25519-ключ, проверяет API certificate fingerprint и SSH host key, включает RDP и регистрирует Scheduled Task.

## 5. Подключение

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

Первый ПК обычно получает `53389`, следующий — `53390` и так далее.

Проверяйте подключение из другой сети, например через мобильный интернет телефона.

## 6. Финальная проверка

- устройство отображается онлайн в Telegram;
- `ssh.exe` работает на Windows;
- назначенный порт слушается на сервере;
- RDP открывается из другой сети;
- после перезагрузки Windows туннель восстанавливается автоматически;
- второй ПК получает отдельный порт и отдельный ключ.

Полная процедура: [TESTING_A_TO_Z.md](TESTING_A_TO_Z.md).
