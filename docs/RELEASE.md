# Release process

## Подготовка

1. Обновить `VERSION` и `CHANGELOG.md`.
2. Запустить локальную проверку:

```bash
bash scripts/check-release.sh
```

3. Открыть pull request и дождаться зелёного CI для Linux и Windows.

## Публикация

После слияния в `main` создать тег, совпадающий с `VERSION`:

```bash
git tag -a "v$(cat VERSION)" -m "Hermes RDP v$(cat VERSION)"
git push origin "v$(cat VERSION)"
```

Затем создать GitHub Release из этого тега и использовать соответствующий раздел `CHANGELOG.md` как описание.

Проект не хранит бинарники FRP в репозитории: установщики скачивают закреплённую официальную версию и проверяют SHA-256.
