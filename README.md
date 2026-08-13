# Hermes RDP

**Hermes RDP** — self-hosted система для управления удалённым доступом к нескольким Windows-компьютерам через один Linux-сервер и Telegram.

[Сайт](https://hermes-rdp.vercel.app/) · [Документация](docs/INDEX.md) · [Безопасность](docs/SECURITY.md)

## Что уже подтверждено

- установка Linux-сервера;
- добавление нескольких Windows-ПК;
- постоянный endpoint для каждого компьютера;
- внешний Microsoft Remote Desktop;
- восстановление после перезагрузок;
- Telegram-команды `OFF`, `ON`, `RESTART`;
- Windows 10 и Windows Server 2019;
- безопасное обновление server/client с rollback;
- отдельный Repair существующего клиента;
- повторная выдача одноразового pairing-кода.

Подробный список фактически проверенных сценариев: [docs/VALIDATED_SCENARIOS.md](docs/VALIDATED_SCENARIOS.md).

## Пользовательский flow

**➕ ДОБАВИТЬ ПК** используется для нового компьютера.

Если одноразовый код истёк или уже использован, нажмите **🔁 НОВЫЙ КОД**.

Если компьютер уже зарегистрирован, используйте **🛠 ВОССТАНОВИТЬ КЛИЕНТ** в его карточке. Repair сохраняет существующую регистрацию и назначенный endpoint.

## Документация

- [Быстрый старт](docs/QUICKSTART.md)
- [Установка сервера](docs/INSTALL_SERVER.md)
- [Установка Windows](docs/INSTALL_WINDOWS.md)
- [Архитектура](docs/ARCHITECTURE.md)
- [Эксплуатация](docs/OPERATIONS.md)
- [Диагностика](docs/TROUBLESHOOTING.md)
- [Проверенные сценарии](docs/VALIDATED_SCENARIOS.md)
- [Модель безопасности](docs/SECURITY.md)

## Релизный статус

Текущий опубликованный релиз: [`v1.1.0`](https://github.com/bakunity/RDP/releases/tag/v1.1.0).

`v1.2.0` находится в подготовке. Версия и новый release tag будут опубликованы отдельным финальным release PR после синхронизации документации и зелёного CI.

Лицензия: [MIT](LICENSE).
