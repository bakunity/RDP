# Changelog

Все заметные изменения проекта фиксируются здесь. Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/), версии следуют Semantic Versioning.

## [Unreleased]

### Документация и сайт

- публичная страница полностью переведена с устаревшего описания FRP на текущую OpenSSH-архитектуру;
- добавлен блок реально подтверждённых сценариев: чистая установка, Windows pairing и внешний RDP через мобильную сеть;
- README, quickstart, установка, архитектура, эксплуатация, диагностика, безопасность и миграция переписаны по результатам живого теста;
- acceptance checklist теперь отдельно показывает уже пройденные и ещё не закрытые проверки;
- добавлены regression tests, запрещающие возврат `v1.0.7`, `FRPC` и `FRPS` на публичную страницу;
- release-check стал совместим с системным Python 3.10 без внешнего `tomllib`.

## [1.1.0] — 2026-08-06

Релиз: https://github.com/bakunity/RDP/releases/tag/v1.1.0

Крупный релиз: транспорт Hermes RDP переведён с FRP на системный OpenSSH.

### Добавлено

- отдельный изолированный `sshd` на порту `7000/tcp`;
- индивидуальный Ed25519-ключ и постоянный RDP-порт для каждого ПК;
- динамический `AuthorizedKeysCommand` с `permitlisten` только на назначенный порт;
- закрепление SSH host key через уже закреплённый HTTPS API;
- автоматическое восстановление reverse SSH-туннеля после обрыва или перезагрузки;
- атомарный pairing, отзыв SSH-ключа и повторное использование освобождённых портов.

### Изменено

- Windows использует встроенные `ssh.exe` и `ssh-keygen.exe`;
- Telegram ON/OFF/RESTART управляет OpenSSH-туннелем;
- OFF и DELETE закрывают активный listener на сервере;
- миграция с `v1.0.x` выполняется явно через `--migrate`.

### Удалено

- `frps`, `frpc.exe`, загрузка стороннего FRP-архива и Defender exclusions.

### Безопасность

- tunnel-user не получает shell, PTY, SFTP, agent forwarding или произвольные порты;
- private key остаётся только на Windows-ПК;
- удаление устройства отзывает API-token и SSH public key.

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

- публичные команды и стандартные порты не изменены;
- исправление затрагивает только ветку чистой серверной установки.

## [1.0.2] — 2026-08-06

Hotfix загрузки FRP Windows-клиентом при ложном срабатывании Microsoft Defender.

### Исправлено

- добавлена явная диагностика Defender quarantine по событиям 1116/1117;
- FRP-загрузка выполняется до расходования pairing-кода;
- cleanup временных файлов не перекрывает исходную ошибку установки;
- при обнаружении quarantine показывается понятное сообщение без автоматического ослабления Defender.

## [1.0.1] — 2026-08-05

Hotfix bootstrap Windows-установщика.

### Исправлено

- Telegram-команда загружает PowerShell-установщик без сохранения во временный файл;
- сохранена проверка TLS fingerprint;
- исправлена совместимость PowerShell 5.1.

## [1.0.0] — 2026-08-05

Первый публичный релиз Hermes RDP.

### Добавлено

- Linux controller и FRP gateway;
- Windows agent и FRPC client;
- Telegram dashboard;
- SQLite registry;
- HTTPS API с TLS pinning;
- multi-PC support;
- диагностика и release automation.
