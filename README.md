# Hermes RDP

**Hermes RDP** — self-hosted шлюз для доступа к нескольким Windows-компьютерам через один Linux-сервер. Транспорт построен на системном OpenSSH: Windows использует встроенный `ssh.exe`, а сервер запускает отдельный изолированный `sshd`.

[Сайт](https://hermes-rdp.vercel.app/) · [Исходники](https://github.com/bakunity/RDP) · [Документация](docs/INDEX.md) · [Безопасность](docs/SECURITY.md)

## Что уже проверено

- чистая установка на Debian/Ubuntu;
- Telegram pairing и повторная выдача одноразового кода;
- регистрация нескольких Windows-ПК и уникальные Ed25519-ключи;
- reverse SSH-туннель и постоянный внешний RDP endpoint на каждый ПК;
- внешний Microsoft Remote Desktop через отдельную сеть;
- одновременная работа нескольких Windows-устройств;
- восстановление после перезагрузки Windows и Linux-сервера;
- Telegram-команды `OFF`, `ON`, `RESTART`;
- hard delete устройства, отзыв ключа/token и безопасное повторное использование освобождённого порта;
- Windows 10 x64 из 32-битного PowerShell через native OpenSSH/Sysnative;
- Windows Server 2019;
- transactional server/client update с автоматическим rollback;
- отдельный Repair существующего клиента без повторного pairing и без смены identity/порта;
- работа без `frpc.exe` и без ослабления Microsoft Defender.

Подробности: [проверенные сценарии](docs/VALIDATED_SCENARIOS.md).

## Схема

```text
Windows PC 1 -- ssh -R --> SERVER:53389 --> 127.0.0.1:3389
Windows PC 2 -- ssh -R --> SERVER:53390 --> 127.0.0.1:3389
Windows PC 3 -- ssh -R --> SERVER:53391 --> 127.0.0.1:3389
```

Каждый компьютер получает отдельные:

- Ed25519-ключ, создаваемый локально;
- постоянный RDP-порт;
- API-token;
- запись и управление в Telegram;
- задачу `Hermes RDP Agent` от имени `SYSTEM`.

Приватный ключ не передаётся серверу. Сервер хранит public key и разрешает ему слушать только назначенный порт через `permitlisten`.

## Компоненты

| Компонент | Назначение |
|---|---|
| `hermes-rdp-sshd.service` | отдельный OpenSSH daemon для reverse-туннелей |
| `hermes-rdp.service` | HTTPS API, Telegram bot и registry |
| SQLite | pairing-коды, устройства, команды и телеметрия |
| Windows OpenSSH Client | `ssh.exe` и `ssh-keygen.exe` |
| `HermesRdpAgent.ps1` | туннель, heartbeat, команды и LIVE-метрики |

## Порты по умолчанию

| Порт | Назначение |
|---:|---|
| `7000/tcp` | OpenSSH-туннели |
| `7443/tcp` | HTTPS API |
| `53389–53420/tcp` | внешние RDP endpoints |

Стандартный пул рассчитан на 32 устройства и расширяется параметрами установщика.

## Быстрый старт

### 1. Сервер

Для production используйте опубликованный release tag или другой заранее проверенный immutable ref, а не изменяемый `main`.

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

### 2. Проверка

```bash
sudo hermes-rdpctl doctor
sudo systemctl status hermes-rdp-sshd.service hermes-rdp.service --no-pager
```

### 3. Windows

Отправьте `/start` Telegram-боту и нажмите **➕ ДОБАВИТЬ ПК**. Fresh pairing предназначен только для нового клиента. Если Hermes уже зарегистрирован на ПК, используйте отдельную кнопку **🛠 ВОССТАНОВИТЬ КЛИЕНТ** в карточке существующего устройства.

Если одноразовый pairing-код истёк или уже использован, нажмите **🔁 НОВЫЙ КОД** и используйте обновлённую команду.

### 4. RDP

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

## Обновление и repair

Server и Windows updater выполняют backup перед runtime mutation и автоматически пытаются восстановить предыдущую рабочую схему при ошибке после mutation.

Repair существующего Windows-клиента:

- не создаёт новое устройство;
- не выполняет новый pairing;
- сохраняет `device.json`, API-token, Ed25519 identity, `known_hosts` и назначенный RDP-порт;
- может восстановить отсутствующий/сломанный Hermes Agent и Scheduled Task;
- при ошибке после mutation откатывает предыдущие agent/task.

Если потеряны `device.json`, private key или `known_hosts`, обычный Repair намеренно останавливается: автоматическое восстановление identity в этот flow не входит.

## Важная граница безопасности

Hermes защищает регистрацию, ключи и туннель, но конечный endpoint остаётся RDP-портом Windows. Используйте сильные уникальные пароли, обновляйте Windows, включайте NLA и ограничивайте источники через firewall там, где это возможно.

## Документация

- [Индекс по ролям](docs/INDEX.md)
- [Быстрый старт](docs/QUICKSTART.md)
- [Установка сервера](docs/INSTALL_SERVER.md)
- [Установка Windows](docs/INSTALL_WINDOWS.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Эксплуатация](docs/OPERATIONS.md)
- [Диагностика](docs/TROUBLESHOOTING.md)
- [Тестирование от А до Я](docs/TESTING_A_TO_Z.md)
- [Модель безопасности](docs/SECURITY.md)
- [Миграция с FRP](docs/MIGRATION.md)

## Релизный статус

Текущий опубликованный release — `v1.1.0`. Стабилизационный `v1.2.0` готовится отдельно: release tag не должен публиковаться до финальной синхронизации версии, документации, release notes и зелёного release CI.

Лицензия: [MIT](LICENSE).
