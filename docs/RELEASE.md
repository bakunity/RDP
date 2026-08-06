# Процесс релиза

Hermes RDP использует Semantic Versioning и автоматическую публикацию GitHub Release после merge релизного PR в `main`.

## Источники версии

Версия должна совпадать в четырёх местах:

```text
VERSION
server/hermes_rdp/__init__.py
server/pyproject.toml
docs/releases/vX.Y.Z.md
```

API `/healthz` берёт version из `hermes_rdp.__version__`, поэтому отдельную строку в `api.py` менять не нужно.

## Что обновлять в релизном PR

1. `VERSION`;
2. `server/hermes_rdp/__init__.py`;
3. `server/pyproject.toml`;
4. `CHANGELOG.md`;
5. `docs/releases/vX.Y.Z.md`;
6. README, если изменились команды или требования;
7. migration/security docs, если затронут deployment contract.

## Локальная проверка

```bash
bash scripts/check-release.sh
```

Проверяются:

- Bash syntax;
- Python compile;
- unit tests;
- согласованность version files;
- наличие release notes;
- отсутствие управляющих символов в Markdown/PowerShell;
- корректность ссылок на текущий release tag в основных документах.

PowerShell parse дополнительно выполняется Windows job в GitHub Actions.

## Pull request

Релизный PR должен содержать:

- краткое резюме;
- breaking changes;
- migration plan;
- security impact;
- результаты Linux и Windows CI;
- план отката;
- ссылку на release notes.

Merge запрещён при красном CI.

## Автоматическая публикация

Workflow `.github/workflows/release.yml` запускается после изменения `VERSION`/release notes в `main`.

Алгоритм:

1. читает `VERSION`;
2. формирует tag `vX.Y.Z`;
3. проверяет version consistency;
4. ищет `docs/releases/vX.Y.Z.md`;
5. создаёт annotated tag, если его нет;
6. создаёт GitHub Release из release notes, если его нет;
7. не перезаписывает существующий tag/release.

GitHub Release:

```text
https://github.com/bakunity/RDP/releases/tag/vX.Y.Z
```

Последний релиз:

```text
https://github.com/bakunity/RDP/releases/latest
```

## Ручная публикация

Используется только если automatic workflow недоступен.

```bash
VERSION="$(tr -d '\r\n' < VERSION)"
TAG="v$VERSION"
git tag -a "$TAG" -m "Hermes RDP $TAG"
git push origin "$TAG"
gh release create "$TAG" --title "Hermes RDP $TAG" --notes-file "docs/releases/$TAG.md" --verify-tag
```

## Stable install URLs

Server:

```text
https://raw.githubusercontent.com/bakunity/RDP/vX.Y.Z/scripts/install-server.sh
```

Windows:

```text
https://raw.githubusercontent.com/bakunity/RDP/vX.Y.Z/scripts/install-client.ps1
```

Update scripts:

```text
https://raw.githubusercontent.com/bakunity/RDP/vX.Y.Z/scripts/update-server.sh
https://raw.githubusercontent.com/bakunity/RDP/vX.Y.Z/scripts/update-client.ps1
```

Release commands в README и release notes должны использовать tag, а не `main`.

## Rollback релиза

Не перемещай опубликованный tag на другой commit.

При критической ошибке:

1. пометь release как problematic в notes;
2. подготовь исправление;
3. выпусти PATCH version;
4. при необходимости документируй rollback на предыдущий tag;
5. не переписывай историю стабильного релиза.

## Checklist

- [ ] version согласована;
- [ ] changelog обновлён;
- [ ] release notes созданы;
- [ ] docs и команды используют новый tag;
- [ ] Python tests PASS;
- [ ] Python compile PASS;
- [ ] Bash syntax PASS;
- [ ] Windows PowerShell parse PASS;
- [ ] secrets scan/review выполнен;
- [ ] migration проверена;
- [ ] backup/rollback описаны;
- [ ] PR merge выполнен;
- [ ] tag создан;
- [ ] GitHub Release опубликован;
- [ ] release links открываются;
