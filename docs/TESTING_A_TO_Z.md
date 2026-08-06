# Тестирование Hermes RDP от А до Я

Этот сценарий предназначен для **чистой проверки проекта на отдельном сервере, новом Telegram-боте и новом Windows-ПК**. Он не зависит от существующей production-инфраструктуры и не использует реальные данные владельца проекта.

После прохождения документа будет понятно:

- правильно ли устанавливается сервер;
- отвечает ли новый Telegram-бот;
- регистрируется ли Windows-ПК;
- работает ли постоянный RDP endpoint;
- приходят ли LIVE-метрики;
- работают ли `ON`, `OFF` и `RESTART`;
- переживает ли система перезагрузку Windows и сервера;
- можно ли без путаницы добавить второй ПК;
- какие логи собирать при ошибке.

---

## 1. Что потребуется

### Отдельный Linux-сервер

Поддерживаемая среда:

- Ubuntu или Debian;
- архитектура `x86_64`;
- публичный IPv4 или DNS-имя;
- пользователь с `sudo`;
- `systemd`;
- доступ сервера к GitHub и Telegram API.

Минимально для теста:

- 1 vCPU;
- 1 ГБ RAM;
- 2 ГБ свободного диска.

### Новый Windows-ПК

- 64-битная Windows 10/11 Pro, Enterprise или Education;
- PowerShell 5.1+;
- права администратора;
- доступ к GitHub и тестовому серверу;
- Windows-пользователь с паролем для RDP.

Windows Home не поддерживает штатный входящий RDP-host.

### Новый Telegram-бот

Понадобятся:

- token нового бота;
- числовой Telegram user ID владельца теста.

Не публикуй token в issue, README, скриншотах или сообщениях разработчикам.

---

## 2. Переменные, используемые в инструкции

Во всех примерах используются только шаблонные значения:

| Переменная | Что подставить |
|---|---|
| `SERVER_IP_OR_DOMAIN` | публичный IP или DNS тестового сервера |
| `TELEGRAM_BOT_TOKEN` | token нового Telegram-бота |
| `TELEGRAM_USER_ID` | числовой Telegram ID владельца |
| `Windows-PC-01` | любое понятное имя первого тестового ПК |
| `PAIR_CODE` | одноразовый код регистрации |
| `API_FINGERPRINT` | SHA-256 fingerprint API-сертификата |
| `53389` | постоянный RDP-порт первого ПК |

Порты проекта по умолчанию:

```text
7000/tcp          FRP control
7443/tcp          HTTPS API
53389-53420/tcp   RDP endpoints
```

---

## 3. Подготовить новый Telegram-бот

Создай нового бота через официальный BotFather и сохрани token.

Отправь созданному боту любое сообщение, например:

```text
/start
```

На Linux-сервере безопасно считать token в переменную:

```bash
read -rsp 'Telegram bot token: ' TG_TOKEN; echo
```

Посмотреть последние Telegram updates:

```bash
curl -fsSL "https://api.telegram.org/bot${TG_TOKEN}/getUpdates" | python3 -m json.tool
```

Найди числовое значение:

```json
"from": {
  "id": 123456789
}
```

Это и есть `TELEGRAM_USER_ID`.

После установки Hermes RDP bot сам переключится на long polling.

---

## 4. Проверить чистоту тестового сервера

Подключись по SSH:

```bash
ssh SERVER_USER@SERVER_IP_OR_DOMAIN
```

Проверить ОС:

```bash
cat /etc/os-release
```

Проверить архитектуру:

```bash
uname -m
```

Ожидается:

```text
x86_64
```

Проверить занятость портов:

```bash
sudo ss -lntp | grep -E ':(7000|7443|53389)\b' || true
```

На чистом сервере вывод должен быть пустым.

Проверить свободный диск:

```bash
df -h /
```

---

## 5. Задать локальные переменные сервера

Вставь значения только в своей SSH-сессии:

```bash
export HERMES_RDP_VERSION='v1.0.6'
export SERVER_HOST='SERVER_IP_OR_DOMAIN'
export TELEGRAM_USER_ID='123456789'
```

Token уже должен находиться в переменной `TG_TOKEN` после предыдущего шага.

Проверить переменные без вывода token:

```bash
printf 'VERSION=%s\nSERVER=%s\nTELEGRAM_USER_ID=%s\n' "$HERMES_RDP_VERSION" "$SERVER_HOST" "$TELEGRAM_USER_ID"
```

---

## 6. Скачать стабильный серверный установщик

```bash
curl -fsSL "https://raw.githubusercontent.com/bakunity/RDP/${HERMES_RDP_VERSION}/scripts/install-server.sh" -o /tmp/install-hermes-rdp.sh
```

Проверить, что файл существует:

```bash
ls -lh /tmp/install-hermes-rdp.sh
```

Проверить Bash-синтаксис:

```bash
bash -n /tmp/install-hermes-rdp.sh
```

Ожидается отсутствие ошибок.

---

## 7. Установить Hermes RDP на новый сервер

```bash
sudo env HERMES_RDP_REF="$HERMES_RDP_VERSION" bash /tmp/install-hermes-rdp.sh \
  --host "$SERVER_HOST" \
  --telegram-token "$TG_TOKEN" \
  --telegram-chat-id "$TELEGRAM_USER_ID"
```

Установщик должен:

1. установить зависимости;
2. скачать и проверить FRP;
3. создать TLS для API и FRP;
4. установить серверный Python-код;
5. создать SQLite registry;
6. установить `frps.service`;
7. установить `hermes-rdp.service`;
8. открыть стандартные порты через UFW;
9. запустить обе службы;
10. показать API fingerprint.

После установки очистить token и временный файл:

```bash
unset TG_TOKEN
rm -f /tmp/install-hermes-rdp.sh
```

---

## 8. Проверить сервер после установки

### Встроенная диагностика

```bash
sudo hermes-rdpctl doctor
```

Ожидаемый результат:

```text
config: OK (...)
database: OK (...)
api: OK (1.0.6)
frp-control: LISTEN 7000
api: LISTEN 7443
```

### systemd

```bash
sudo systemctl status frps.service hermes-rdp.service --no-pager
```

Обе службы должны быть:

```text
active (running)
```

### Порты

```bash
sudo ss -lntp | grep -E ':(7000|7443)\b'
```

### Firewall

```bash
sudo ufw status numbered
```

Должны присутствовать правила для:

```text
7000/tcp
7443/tcp
53389:53420/tcp
```

### API

```bash
curl -k "https://127.0.0.1:7443/healthz" | python3 -m json.tool
```

Ожидается:

```json
{
  "ok": true,
  "service": "hermes-rdp",
  "version": "1.0.6",
  "fingerprint": "..."
}
```

---

## 9. Проверить нового Telegram-бота

Открой Telegram и отправь новому боту:

```text
/start
```

Должно появиться одно сообщение dashboard:

```text
HERMES RDP · КОМПЬЮТЕРЫ
Онлайн: 0 из 0
```

Кнопки:

```text
ДОБАВИТЬ ПК
REFRESH
LIVE 3s
```

### PASS

- бот отвечает;
- создаётся только одно dashboard-сообщение;
- `/start` не создаёт бесконечный поток сообщений;
- `REFRESH` редактирует существующее сообщение.

### FAIL

Если бот молчит:

```bash
sudo journalctl -u hermes-rdp.service -n 100 --no-pager
```

---

## 10. Создать код для первого ПК

На сервере:

```bash
export PC_NAME='Windows-PC-01'
PAIR_OUTPUT="$(sudo hermes-rdpctl pair create --name "$PC_NAME" --port 53389)"
printf '%s\n' "$PAIR_OUTPUT"
```

Ожидается:

```text
PAIR_CODE=XXXXXXXX
EXPIRES_IN=900
SERVER=SERVER_IP_OR_DOMAIN
FINGERPRINT=API_FINGERPRINT
```

Сохранить значения в текущей SSH-сессии:

```bash
export PAIR_CODE="$(printf '%s\n' "$PAIR_OUTPUT" | sed -n 's/^PAIR_CODE=//p')"
export API_FINGERPRINT="$(printf '%s\n' "$PAIR_OUTPUT" | sed -n 's/^FINGERPRINT=//p')"
```

Проверить без раскрытия других secrets:

```bash
printf 'PAIR_CODE=%s\nAPI_FINGERPRINT=%s\n' "$PAIR_CODE" "$API_FINGERPRINT"
```

Pair code действует 15 минут и используется один раз.

---

## 11. Установить клиент на новом Windows-ПК

Открой **Windows PowerShell от имени администратора**.

Задай переменные:

```powershell
$Version = 'v1.0.6'
$Server = 'SERVER_IP_OR_DOMAIN'
$PairCode = 'PAIR_CODE'
$Fingerprint = 'API_FINGERPRINT'
$PcName = 'Windows-PC-01'
```

Запусти установку:

```powershell
$InstallerUrl = "https://raw.githubusercontent.com/bakunity/RDP/$Version/scripts/install-client.ps1"
& ([scriptblock]::Create((irm $InstallerUrl))) `
  -Server $Server `
  -PairCode $PairCode `
  -Fingerprint $Fingerprint `
  -Name $PcName `
  -RepositoryRef $Version
```

Установщик должен показать:

```text
ГОТОВО
Компьютер: Windows-PC-01
RDP: SERVER_IP_OR_DOMAIN:53389
Устройство: <device_id>
Задача: Hermes RDP Agent
Лог: C:\ProgramData\HermesRDP\agent.log
```

---

## 12. Проверить Windows-клиент

### Scheduled Task

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

Ожидается:

```text
State: Running
```

### Task info

```powershell
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
```

`LastTaskResult` должен быть `0` или task должна продолжать работать без завершения.

### Agent log

```powershell
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

### FRPC

```powershell
Get-Process frpc -ErrorAction SilentlyContinue
```

### Локальный RDP

```powershell
Get-Service TermService
```

```powershell
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

### Связь с сервером

```powershell
Test-NetConnection $Server -Port 7000
```

```powershell
Test-NetConnection $Server -Port 7443
```

Оба теста должны показать:

```text
TcpTestSucceeded : True
```

---

## 13. Проверить Telegram LIVE-данные

Подожди 5–15 секунд и нажми `REFRESH`.

Первый ПК должен появиться как:

```text
Windows-PC-01 · :53389
ONLINE
```

На экране устройства проверить:

- имя ПК;
- редакцию Windows;
- пользователя или активную session;
- CPU;
- RAM;
- диск C;
- сеть;
- uptime;
- FRPC state;
- endpoint state;
- RDP sessions;
- top processes.

### PASS

- данные обновляются примерно раз в 3 секунды;
- dashboard не создаёт новые сообщения;
- возраст данных не растёт постоянно;
- устройство не переключается случайно в OFFLINE.

---

## 14. Проверить публичный RDP endpoint

Тест нужно выполнять **с другого устройства**, а не с самого target-PC.

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

Ожидается:

```text
TcpTestSucceeded : True
```

Открыть RDP:

```powershell
mstsc.exe /v:SERVER_IP_OR_DOMAIN:53389
```

Войти под обычной Windows-учётной записью тестового ПК.

### PASS

- открывается Windows login;
- авторизация проходит;
- Telegram показывает активную RDP-сессию;
- внешний client address отображается шаблонно как реальный адрес подключившегося клиента, но не должен попадать в публичную документацию.

---

## 15. Проверить кнопку OFF

В Telegram открой `Windows-PC-01` и нажми:

```text
OFF
```

Подожди до 10 секунд.

На внешнем устройстве:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

Ожидается:

```text
TcpTestSucceeded : False
```

Telegram должен продолжать получать telemetry, потому что выключается только FRPC, а не Windows agent.

### PASS

- endpoint закрывается;
- устройство остаётся ONLINE;
- метрики продолжают обновляться;
- другие устройства не затрагиваются.

---

## 16. Проверить кнопку ON

Нажми:

```text
ON
```

Подожди до 10 секунд.

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

Ожидается:

```text
TcpTestSucceeded : True
```

---

## 17. Проверить кнопку RESTART

Нажми:

```text
RESTART
```

Endpoint может кратковременно закрыться и снова открыться.

Проверить через несколько секунд:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

Ожидается:

```text
TcpTestSucceeded : True
```

На Windows должен измениться PID `frpc.exe`.

---

## 18. Проверить перезагрузку Windows

На тестовом ПК:

```powershell
Restart-Computer
```

После загрузки подожди 30–60 секунд.

Проверить:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
```

```powershell
Get-Process frpc -ErrorAction SilentlyContinue
```

В Telegram ПК снова должен стать ONLINE, endpoint — доступным.

### PASS

- ручной запуск ничего не требует;
- task стартует от `SYSTEM`;
- FRPC запускается автоматически;
- RDP port остаётся `53389`.

---

## 19. Проверить перезапуск controller

На Linux-сервере:

```bash
sudo systemctl restart hermes-rdp.service
```

Сразу проверить RDP endpoint с внешнего ПК.

Он должен продолжить работать, потому что FRPS не останавливался.

Telegram может несколько секунд не обновляться, затем восстановиться.

### PASS

- RDP tunnel не падает из-за restart controller;
- bot снова отвечает;
- telemetry восстанавливается.

---

## 20. Проверить перезапуск FRPS

На сервере:

```bash
sudo systemctl restart frps.service
```

Все endpoints кратковременно закроются. FRPC должен автоматически переподключиться.

Через 10–30 секунд:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
```

Ожидается `True`.

---

## 21. Добавить второй ПК

На втором Windows-компьютере повтори установку через кнопку:

```text
ДОБАВИТЬ ПК
```

Или на сервере:

```bash
sudo hermes-rdpctl pair create --name 'Windows-PC-02'
```

Сервер должен автоматически выдать:

```text
53390
```

Ожидаемый dashboard:

```text
Windows-PC-01 · :53389
Windows-PC-02 · :53390
```

Проверить независимо:

```powershell
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53389
Test-NetConnection SERVER_IP_OR_DOMAIN -Port 53390
```

Нажать OFF у первого ПК и убедиться, что второй endpoint остаётся доступным.

Это главный Multi-PC тест.

---

## 22. Проверить удаление устройства

В Telegram выбери тестовый ПК:

```text
УДАЛИТЬ
```

Подтверди удаление.

На сервере:

```bash
sudo hermes-rdpctl devices list
```

Удалённое устройство не должно отображаться как active.

На Windows локальный agent нужно удалить отдельно:

```powershell
$Version = 'v1.0.6'
$Url = "https://raw.githubusercontent.com/bakunity/RDP/$Version/scripts/uninstall-client.ps1"
& ([scriptblock]::Create((irm $Url)))
```

Проверить отсутствие task:

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent' -ErrorAction SilentlyContinue
```

---

## 23. Финальная серверная диагностика

```bash
sudo hermes-rdpctl doctor
```

```bash
sudo systemctl status frps.service hermes-rdp.service --no-pager
```

```bash
sudo journalctl -u frps.service -n 100 --no-pager
```

```bash
sudo journalctl -u hermes-rdp.service -n 150 --no-pager
```

```bash
sudo ufw status numbered
```

---

## 24. Итоговый acceptance checklist

Система считается прошедшей тест, когда выполнены все пункты:

- [ ] сервер устанавливается без ручного редактирования файлов;
- [ ] `hermes-rdpctl doctor` показывает PASS;
- [ ] новый бот отвечает на `/start`;
- [ ] dashboard использует одно сообщение;
- [ ] первый Windows-ПК регистрируется с первого раза;
- [ ] ПК становится ONLINE не позднее 15 секунд;
- [ ] LIVE-метрики обновляются;
- [ ] endpoint `53389` доступен;
- [ ] реальное RDP-подключение проходит;
- [ ] OFF закрывает только выбранный endpoint;
- [ ] ON возвращает endpoint;
- [ ] RESTART перезапускает выбранный FRPC;
- [ ] Windows reboot не требует ручного запуска;
- [ ] restart controller не ломает RDP tunnel;
- [ ] restart FRPS завершается автоматическим reconnect;
- [ ] второй ПК получает `53390`;
- [ ] OFF первого ПК не влияет на второй;
- [ ] удаление отзывает device и освобождает port;
- [ ] в публичных документах нет реальных IP, usernames и machine names.

---

## 25. Что прислать разработчику при FAIL

### С Linux-сервера

```bash
sudo hermes-rdpctl doctor
sudo systemctl --no-pager --full status frps.service hermes-rdp.service
sudo journalctl -u frps.service -n 100 --no-pager
sudo journalctl -u hermes-rdp.service -n 150 --no-pager
sudo hermes-rdpctl devices list
```

### С Windows

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent' | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName 'Hermes RDP Agent'
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 150
Get-Process frpc -ErrorAction SilentlyContinue | Select-Object Id,StartTime,Path
Get-Service TermService
Get-NetTCPConnection -LocalPort 3389 -State Listen -ErrorAction SilentlyContinue
```

Перед отправкой замени:

- публичный IP на `SERVER_IP_OR_DOMAIN`;
- Windows username на `WINDOWS_USER`;
- имя компьютера на `WINDOWS-PC-01`;
- внешний client IP на `CLIENT_IP_ADDRESS`.

Никогда не отправляй:

- Telegram bot token;
- `device.json`;
- `frpc.toml`;
- FRP token;
- private keys;
- server backup;
- действующий pair code.
