# Hermes RDP — persistent chat context

Эта папка — постоянная точка передачи контекста проекта между чатами/сессиями.

> **Новому чату:** сначала прочитай этот файл, затем остальные файлы из блока «Порядок чтения». Не начинай менять код, документацию, сайт или production, пока не сверишь фактическое состояние GitHub с записанным здесь контекстом.

## Порядок чтения

1. [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) — сжатый контекст всей работы и текущая архитектура.
2. [`CURRENT_STATE.md`](CURRENT_STATE.md) — что подтверждено фактически, что только предполагается, какие баги открыты.
3. [`LATEST_AUDIT.md`](LATEST_AUDIT.md) — последний подробный аудит ON/OFF, dashboard, reliability, документации, README и сайта.
4. [`NEXT_WORK.md`](NEXT_WORK.md) — вектор целей, приоритеты и критерий готового продукта.
5. [`DECISIONS.md`](DECISIONS.md) — важные архитектурные решения и ограничения, которые нельзя потерять.
6. [`SESSION_PROTOCOL.md`](SESSION_PROTOCOL.md) — как обновлять эту папку перед следующим переездом в новый чат.
7. [`HISTORY.md`](HISTORY.md) — крупные этапы развития проекта.

## Репозиторий

- Project: `bakunity/RDP`
- Product: **Hermes RDP**
- Public site: `https://hermes-rdp.vercel.app/`
- Main immediately before context initialization: `6cecc33d520e8bd07c322d660c200a454d17e93f`
- Latest published GitHub Release at context initialization: `v1.1.0`
- Context initialized: **2026-08-07**

## Фраза для нового чата

Достаточно написать:

> Открой `context/README.md` в репозитории `bakunity/RDP`, прочитай весь project handoff и продолжай проект с текущего состояния. Сначала ничего не меняй: сверь GitHub/release и коротко подтверди, что понял архитектуру, открытые баги и следующий этап.

## Правило актуальности

GitHub и реальная инфраструктура всегда важнее этого snapshot. Перед конкретным изменением нужно проверить актуальный `main`, release, нужные файлы и открытые PR/ветки.

Эта папка **не должна содержать секреты**: bot token, pairing code, TLS/API fingerprint, SSH private key, device token, реальные production IP, Telegram numeric IDs и содержимое secret config.