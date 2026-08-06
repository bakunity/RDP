# Maintainer handoff

Короткая карта проекта для разработчика, который впервые открывает репозиторий.

## С чего начать

1. [README](../README.md) — продукт и пользовательский сценарий.
2. [Architecture](ARCHITECTURE.md) — компоненты и потоки данных.
3. [Development](DEVELOPMENT.md) — структура кода и правила изменений.
4. [API](API.md) — контракт Windows agent ↔ server.
5. [Security](SECURITY.md) — модель доверия и secrets.
6. [Operations](OPERATIONS.md) — production runbook.

## Ключевые решения

- только Linux server имеет специальную роль;
- все Windows clients равноправны;
- FRPS работает постоянно;
- ON/OFF управляет FRPC конкретного device;
- команды доставляются в ответе на telemetry POST;
- Telegram UI редактирует одно сообщение;
- SQLite — source of truth для devices, pairing, telemetry и commands;
- release URL должен быть привязан к tag, а не к `main`.

## Production paths

```text
/etc/hermes-rdp/
/etc/frp/
/opt/hermes-rdp/app/
/var/lib/hermes-rdp/state.sqlite3
/var/backups/hermes-rdp/
C:\ProgramData\HermesRDP\
```

## Главные entry points

```text
server/hermes_rdp/service.py       server process
server/hermes_rdp/api.py           HTTPS API
server/hermes_rdp/bot.py           Telegram dashboard
server/hermes_rdp/db.py            Registry and SQLite
server/hermes_rdp/cli.py           hermes-rdpctl
client/HermesRdpAgent.ps1          Windows runtime
scripts/install-server.sh          Linux deployment
scripts/install-client.ps1         Windows deployment
```

## Перед merge

```bash
bash scripts/check-release.sh
```

Дождаться зелёных jobs:

- Linux validation;
- Windows PowerShell 5.1 validation.

## Перед релизом

Обновить `VERSION`, Python package version, `CHANGELOG.md` и `docs/releases/vX.Y.Z.md`. После merge workflow создаёт immutable tag и GitHub Release.

## Не ломать

- endpoint существующего device без migration;
- совместимость `/v1`;
- поддержку Windows PowerShell 5.1;
- protected ACL secrets;
- возможность восстановиться из backup;
- равноправие первого и последующих Windows clients.
