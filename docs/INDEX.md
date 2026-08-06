# Документация Hermes RDP

Документация разделена по роли читателя. Начинай с нужного раздела, а не с исходного кода.

## Пользователю

- [Быстрый старт](QUICKSTART.md) — сервер, первый ПК и следующий ПК по шагам.
- [Тестирование от А до Я](TESTING_A_TO_Z.md) — отдельный сервер, новый бот, новый Windows-ПК и полный acceptance test.
- [Установка Windows](INSTALL_WINDOWS.md) — единый клиент для всех компьютеров.
- [Команды](COMMANDS.md) — короткая шпаргалка для PowerShell и Hermes.
- [Диагностика](TROUBLESHOOTING.md) — что проверять при OFFLINE, закрытом endpoint или молчащем боте.

## Администратору сервера

- [Установка сервера](INSTALL_SERVER.md) — параметры установщика, порты, каталоги и проверка.
- [Миграция](MIGRATION.md) — переход со старой одно-компьютерной схемы.
- [Эксплуатация](OPERATIONS.md) — ежедневный runbook, backup, restore, update и удаление.
- [Безопасность](SECURITY.md) — секреты, TLS, ACL, firewall и ротация FRP token.

## Разработчику

- [Архитектура](ARCHITECTURE.md) — компоненты и жизненный цикл данных.
- [API](API.md) — HTTP endpoints, авторизация и форматы сообщений.
- [Разработка](DEVELOPMENT.md) — структура репозитория, локальный запуск, тесты и правила изменений.
- [Релизы](RELEASE.md) — versioning, CI, тег и GitHub Release.
- [Roadmap](ROADMAP.md) — ограничения v1 и направления развития.

## Релизы

- [Последний GitHub Release](https://github.com/bakunity/RDP/releases/latest)
- [v1.0.6](https://github.com/bakunity/RDP/releases/tag/v1.0.6)
- [Release notes v1.0.6](releases/v1.0.6.md)
- [Changelog](../CHANGELOG.md)

## Важное правило архитектуры

**На Windows нет «главного» или «особенного» клиента.** «Windows-PC-01», ноутбук и любой будущий компьютер устанавливаются одним `install-client.ps1`, запускают один `HermesRdpAgent.ps1` и отличаются только выданными сервером credentials и RDP-портом. Особенным является только Linux-сервер Hermes.
