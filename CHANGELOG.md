# Changelog

Все заметные изменения проекта фиксируются здесь. Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии следуют Semantic Versioning.

## [Unreleased]

Пока нет изменений после `v1.0.7`.

## [1.0.7] — 2026-08-06

Hotfix HTTPS certificate pinning в Windows PowerShell 5.1.

### Исправлено

- PowerShell scriptblock удалён из `ServerCertificateCustomValidationCallback`;
- проверка SHA-256 fingerprint выполняется статическим C# callback без зависимости от PowerShell runspace;
- сетевой запрос больше не завершается общей `HttpRequestException` при корректно доступном сервере;
- fingerprint pinning сохранён: неверный сертификат по-прежнему отклоняется;
- добавлен Windows runtime test с реальным самоподписанным сертификатом;
- добавлены Python regression tests, запрещающие возврат PowerShell callback.

### Совместимость

- API, SQLite registry, pairing contract, FRP и стандартные порты не изменены;
- `install-client.ps1` остаётся совместимым с Windows PowerShell 5.1.

## [1.0.6] — 2026-08-06

Hotfix запуска Windows-установщика через Telegram-команду в PowerShell 5.1.

### Исправлено

- перед `ScriptBlock.Create()` удаляется декодированный UTF-8 BOM (`U+FEFF`);
- начальный `param(...)` установщика снова корректно распознаётся при загрузке через `irm`;
- Telegram-команда остаётся компактной, многострочной и копируется одним нажатием;
- regression test проверяет наличие BOM-нормализации и запрещает возврат прямого `Create((irm $u))`.

### Совместимость

- сам `install-client.ps1` остаётся в UTF-8 BOM для корректной работы русского текста в Windows PowerShell 5.1;
- API, SQLite registry, pairing contract, FRP и стандартные порты не изменены.

## [1.0.5] — 2026-08-06

UX-патч компактной команды Telegram и исправление обновления активного сервиса.

### Изменено

- команда Windows-установщика остаётся одним копируемым блоком, но разбита на короткие строки через PowerShell splatting;
- убрана чрезмерная ширина Telegram code block;
- команда не использует хрупкие символы продолжения строки PowerShell;
- повторный запуск серверного установщика явно перезапускает уже активные `frps` и `hermes-rdp`;
- `update-server.sh` корректно загружает как ветки, так и release-теги;
- добавлены regression tests Telegram-разметки и поведения обновления.

### Совместимость

- pairing contract, API, SQLite, FRP-протокол и Windows agent не изменены;
- стандартные порты не изменены.

## [1.0.4] — 2026-08-06

UX-патч Telegram-экрана добавления Windows-ПК.

### Изменено

- команда установки выводится единым моноширинным блоком Telegram;
- всю PowerShell-команду можно скопировать одним нажатием;
- включён HTML parse mode для отправки и редактирования панели;
- команда HTML-экранируется, поэтому `&`, ссылки и другие специальные символы не ломают сообщение;
- добавлены regression tests формата команды и Telegram payload.

### Совместимость

- API, SQLite registry, pairing contract, FRP и Windows agent не изменены;
- обновление затрагивает только отображение Telegram-панели;
- стандартные порты не изменены.

## [1.0.3] — 2026-08-06

Hotfix чистой серверной установки после проверки на отдельном Debian-сервере.

### Исправлено

- установщик больше не запускает `sed` по отсутствующему `/etc/frp/frps.toml`;
- чтение legacy FRP token выполняется только при наличии старого конфигурационного файла;
- чистая установка больше не завершается с `exit=2` до создания systemd-служб;
- добавлен regression test структуры clean-install ветки.

### Совместимость

- повторный запуск после частичной установки `v1.0.2` безопасен;
- существующий сгенерированный FRP token сохраняется;
- API, SQLite, pairing contract и порты не изменены.

## [1.0.2] — 2026-08-06

Hotfix серверного установщика для корректной установки из стабильного Git-тега.

### Исправлено

- загрузка исходников больше не использует `refs/heads/$REF`, из-за чего тег `v1.0.1` ошибочно обрабатывался как ветка и возвращал HTTP 404;
- архив проекта теперь загружается через универсальный endpoint `codeload.github.com`, работающий и с ветками, и с тегами;
- release checks блокируют возврат ошибочного URL с `refs/heads/$REF`.

### Совместимость

- API, SQLite registry, pairing contract и Windows agent не изменены;
- порты `7000`, `7443` и `53389–53420` не изменены;
- обновление является безопасным PATCH-релизом.

## [1.0.1] — 2026-08-06

Документационный и privacy-патч для безопасного публичного тестирования проекта.

### Добавлено

- пошаговый сценарий [тестирования от А до Я](docs/TESTING_A_TO_Z.md) на отдельном сервере, новом Telegram-боте и новом Windows-ПК;
- acceptance checklist для server install, Telegram dashboard, telemetry, RDP, ON/OFF/RESTART, reboot и Multi-PC;
- готовые диагностические команды для Linux и Windows;
- постоянный CI-сканер `scripts/check-public-examples.py`, блокирующий случайно добавленные публичные IP-адреса;
- privacy scan в `scripts/check-release.sh`.

### Изменено

- реальные IP-адреса, machine names, usernames и client addresses заменены на нейтральные переменные;
- примеры используют `SERVER_IP_OR_DOMAIN`, `WINDOWS-PC-01`, `WINDOWS_USER` и `CLIENT_IP_ADDRESS`;
- пользовательские команды обновлены до стабильного тега `v1.0.1`;
- описание релиза `v1.0.0` также очищено от project-specific примеров;
- первый Windows-ПК в документации больше не связан с конкретным владельцем или инфраструктурой.

### Совместимость

- серверный API и Windows agent остаются обратно совместимыми с `v1.0.0`;
- стандартные порты `7000`, `7443` и `53389–53420` не изменены;
- формат SQLite и pairing contract не изменены;
- обновление является безопасным PATCH-релизом.

## [1.0.0] — 2026-08-06

Первый стабильный проектный релиз Hermes RDP.

### Добавлено

- единый Linux-сервер Hermes как управляющий узел;
- одинаковый Windows-клиент для основного и дополнительных ПК;
- автоматическая регистрация устройств по одноразовому восьмисимвольному коду;
- автоматическое распределение постоянных RDP-портов;
- возможность сохранить `53389` за первым Windows-ПК при миграции;
- отдельные `device_id`, API tokens, FRP proxy names и очереди команд;
- Telegram Multi-PC dashboard в одном редактируемом сообщении;
- ONLINE/OFFLINE, ON/OFF/RESTART и LIVE-обновление каждые 3 секунды;
- CPU, RAM, диск, сеть, аптайм, пользователь, процессы и RDP-сессии Windows;
- серверный CLI `hermes-rdpctl`;
- HTTPS API с TLS fingerprint pinning;
- FRP `0.70.1` с принудительным TLS и проверкой SHA-256 архивов;
- автоматические резервные копии при установке и обновлении;
- установщики, обновление и удаление для Linux и Windows;
- CI для Python, Bash и Windows PowerShell 5.1;
- полная документация для пользователей, администраторов и разработчиков;
- автоматическая публикация GitHub Release из `VERSION` и release notes.

### Безопасность

- Telegram доступен только заданному числовому user ID;
- pairing code одноразовый и по умолчанию действует 15 минут;
- у каждого устройства отдельный случайный API token;
- сервер хранит только SHA-256 device token;
- Windows secrets закрыты ACL для `SYSTEM` и Administrators;
- API принимает TLS 1.2+;
- FRP-клиенты проверяют собственную CA сервера.

### Известные ограничения

- FRP token общий для всех подключённых устройств;
- удаление устройства отзывает API-доступ, но для полного отзыва скомпрометированного FRP token требуется его ротация и переподключение доверенных ПК;
- Windows-клиент рассчитан на 64-битные Windows Pro, Enterprise или Education с поддержкой входящего RDP.

[Unreleased]: https://github.com/bakunity/RDP/compare/v1.0.7...HEAD
[1.0.7]: https://github.com/bakunity/RDP/releases/tag/v1.0.7
[1.0.6]: https://github.com/bakunity/RDP/releases/tag/v1.0.6
[1.0.5]: https://github.com/bakunity/RDP/releases/tag/v1.0.5
[1.0.4]: https://github.com/bakunity/RDP/releases/tag/v1.0.4
[1.0.3]: https://github.com/bakunity/RDP/releases/tag/v1.0.3
[1.0.2]: https://github.com/bakunity/RDP/releases/tag/v1.0.2
[1.0.1]: https://github.com/bakunity/RDP/releases/tag/v1.0.1
[1.0.0]: https://github.com/bakunity/RDP/releases/tag/v1.0.0
