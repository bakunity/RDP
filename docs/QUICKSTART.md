# Quick start

## Сервер

```bash
curl -fsSL https://raw.githubusercontent.com/bakunity/RDP/main/scripts/install-server.sh | sudo bash
```

После установки задайте Telegram token и разрешённый Telegram user ID по подсказкам установщика.

## Первый и каждый следующий Windows ПК

1. В Telegram нажать `➕ Добавить ПК` или выполнить на сервере:

```bash
sudo hermes-rdpctl pair create --name 'Название ПК'
```

2. Открыть PowerShell от имени администратора на нужном Windows ПК.
3. Выполнить команду, которую выдал сервер или Telegram-бот.
4. Дождаться статуса `ONLINE`.

Для сохранения конкретного порта:

```bash
sudo hermes-rdpctl pair create --name 'Домашний ПК' --port 53389
```

Все Windows-компьютеры используют один и тот же установщик и один и тот же агент. Отличаются только выданными сервером идентификатором, токеном и портом.
