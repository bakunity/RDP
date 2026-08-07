# Hermes RDP — persistent chat context

Эта папка — постоянная точка передачи контекста проекта между чатами/сессиями.

> **Новому чату:** сначала прочитай этот файл, затем остальные файлы из блока «Порядок чтения». Не начинай менять код, документацию, сайт или production, пока не сверишь фактическое состояние GitHub с записанным здесь контекстом.

## Порядок чтения

1. [`LAST_SESSION.md`](LAST_SESSION.md) — что произошло в самом последнем длинном чате и что делать следующим шагом.
2. [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) — сжатый контекст всей работы и текущая архитектура.
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — что подтверждено фактически, что только предполагается, какие баги открыты.
4. [`LATEST_AUDIT.md`](LATEST_AUDIT.md) — последний подробный актуализированный аудит ON/OFF, dashboard, reliability, документации, README и сайта.
5. [`NEXT_WORK.md`](NEXT_WORK.md) — вектор целей, приоритеты и критерий готового продукта.
6. [`DECISIONS.md`](DECISIONS.md) — важные архитектурные решения и ограничения, которые нельзя потерять.
7. [`SESSION_PROTOCOL.md`](SESSION_PROTOCOL.md) — как обновлять эту папку перед следующим переездом в новый чат.
8. [`HISTORY.md`](HISTORY.md) — крупные этапы развития проекта.

## Полный исходный аудит

Если новому чату нужен не только сжатый handoff, но и исходный подробный анализ из предыдущего длинного разговора, сохранён полный snapshot:

- [`archive/2026-08-07-full-product-audit.md`](archive/2026-08-07-full-product-audit.md) — полный большой аудит архитектуры, ON/OFF, telemetry, Telegram UX, tests, reinstall/ACL, update/rollback, docs, README, Website v2, release plan и definition of done.

Это **исторический первоисточник**, а не актуальный state-файл. Некоторые пункты, которые там были TODO, позже уже подтверждены как PASS. Поэтому при конфликте статусов приоритет такой:

```text
реальная инфраструктура / текущий GitHub
        ↓
LAST_SESSION.md
        ↓
CURRENT_STATE.md
        ↓
LATEST_AUDIT.md
        ↓
архивные полные аудиты
```

Архив не обязательно читать целиком при каждом старте нового чата. Он нужен, когда требуется восстановить подробную аргументацию, дизайн dashboard, старые наблюдения или детали последнего большого анализа.

## Репозиторий

- Project: `bakunity/RDP`
- Product: **Hermes RDP**
- Public site: `https://hermes-rdp.vercel.app/`
- Base product `main` immediately before context initialization: `6cecc33d520e8bd07c322d660c200a454d17e93f`
- Latest published GitHub Release at context initialization: `v1.1.0`
- Context initialized: **2026-08-07**
- Latest session handoff refreshed: **2026-08-07** after real reboot + Telegram OFF/ON validation and Windows 10 x64/x86-PowerShell compatibility diagnosis.

## Фраза для нового чата

Достаточно написать:

> Открой `context/README.md` в репозитории `bakunity/RDP`, прочитай основной context по указанному порядку и продолжай проект с текущего состояния. Сначала сверь актуальный GitHub/release/ветки и коротко подтверди, что понял последние подтверждённые тесты, открытые баги и следующий этап. Не повторяй уже пройденные проверки без причины. Если для решения нужна подробная аргументация последнего большого аудита — прочитай `context/archive/2026-08-07-full-product-audit.md`.

## Перед следующим переездом

В конце каждого длинного рабочего чата новый ассистент должен:

1. перезаписать `LAST_SESSION.md` свежим компактным delta-контекстом;
2. обновить `CURRENT_STATE.md`, если появились новые PASS/FAIL;
3. обновить `PROJECT_HANDOFF.md`, если изменились архитектура или ключевой вектор;
4. обновить `NEXT_WORK.md`, если завершились этапы или изменились приоритеты;
5. обновить `LATEST_AUDIT.md`, если был новый глубокий анализ;
6. при действительно крупном новом анализе сохранить его полный snapshot в `context/archive/`, а в актуальных context-файлах оставить сжатые выводы;
7. добавить короткую запись в `HISTORY.md` для значимого milestone;
8. не записывать секреты.

## Правило актуальности

GitHub и реальная инфраструктура всегда важнее snapshot. Перед конкретным изменением нужно проверить актуальный `main`, release, нужные файлы и открытые PR/ветки.

Эта папка **не должна содержать секреты**: bot token, pairing code, TLS/API fingerprint, SSH private key, device token, реальные production IP, Telegram numeric IDs и содержимое secret config.
