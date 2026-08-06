# Hermes RDP API v1

HTTPS API используется только Windows-установщиком и Windows-агентом. Telegram bot работает напрямую с `Registry` внутри серверного процесса и не вызывает HTTP API.

## Базовый адрес

```text
https://PUBLIC_HOST:7443
```

Порт настраивается параметром `--api-port` серверного установщика.

## TLS

API использует TLS 1.2+. Серверный установщик создаёт сертификат и сохраняет SHA-256 fingerprint в:

```text
/etc/hermes-rdp/tls/api.sha256
```

Windows installer и agent не доверяют сертификату «вслепую»: они сверяют точный fingerprint, полученный из доверенного канала Telegram/CLI.

## Ограничения запроса

- `Content-Type: application/json`;
- request body — JSON object;
- максимальный body — 128 KiB;
- ответы содержат `Cache-Control: no-store`;
- device endpoints требуют Bearer token.

## GET `/healthz`

Публичная проверка состояния и fingerprint.

### Ответ `200`

```json
{
  "ok": true,
  "service": "hermes-rdp",
  "version": "1.0.0",
  "fingerprint": "SHA256_HEX"
}
```

Windows installer сравнивает `fingerprint` с ожидаемым значением до pairing.

## POST `/v1/pair`

Одноразовая регистрация нового устройства. Bearer token не требуется, но нужен действующий pair code и корректный TLS fingerprint.

### Запрос

```json
{
  "code": "ABCDEFGH",
  "display_name": "Windows-PC-01",
  "machine_name": "WINDOWS-PC-01",
  "fingerprint": "WINDOWS_MACHINE_UUID"
}
```

Поля:

| Поле | Обязательное | Описание |
|---|---:|---|
| `code` | да | восьмисимвольный одноразовый код |
| `display_name` | нет | удобное имя в Telegram |
| `machine_name` | да | имя Windows-компьютера |
| `fingerprint` | нет | Windows hardware UUID для аудита |

### Ответ `201`

```json
{
  "ok": true,
  "device": {
    "id": "UUID_HEX",
    "name": "Windows-PC-01",
    "rdp_port": 53389,
    "token": "DEVICE_API_TOKEN"
  },
  "api": {
    "base_url": "https://SERVER_IP_OR_DOMAIN:7443",
    "fingerprint": "SHA256_HEX"
  },
  "frp": {
    "server_addr": "SERVER_IP_OR_DOMAIN",
    "server_port": 7000,
    "token": "SHARED_FRP_TOKEN",
    "ca_pem": "-----BEGIN CERTIFICATE-----..."
  }
}
```

Ответ содержит секреты и не должен логироваться или публиковаться.

### Ошибки

- `400 invalid pair code`;
- `400 pair code expired`;
- `400 pair code was already used`;
- `400 no free RDP ports` через общий error path;
- `500 internal server error`.

## POST `/v1/devices/{device_id}/telemetry`

Отправляет текущую телеметрию и получает pending command.

### Авторизация

```http
Authorization: Bearer DEVICE_API_TOKEN
```

Сервер хранит только SHA-256 token и сравнивает его через `secrets.compare_digest`.

### Запрос

```json
{
  "telemetry": {
    "captured_at": 1785980000,
    "computer_name": "WINDOWS-PC-01",
    "os": "Microsoft Windows 11 Pro",
    "interactive_user": "WINDOWS_USER",
    "sessions": ["WINDOWS_USER"],
    "cpu_percent": 9.0,
    "ram_total_bytes": 34198626304,
    "ram_used_bytes": 16857104384,
    "ram_percent": 49.3,
    "disk_total_bytes": 999653638144,
    "disk_used_bytes": 886634086400,
    "disk_percent": 88.7,
    "network_received_bytes": 4080218931,
    "network_sent_bytes": 2866899763,
    "route": "Беспроводная сеть",
    "frpc_running": true,
    "endpoint_available": true,
    "rdp_connections": 1,
    "rdp_remote_addresses": ["CLIENT_IP_ADDRESS"],
    "uptime_seconds": 1379880,
    "top_processes": []
  }
}
```

### Ответ без команды

```json
{
  "ok": true,
  "command": null
}
```

### Ответ с командой

```json
{
  "ok": true,
  "command": {
    "seq": 12,
    "action": "restart",
    "created_at": 1785980010
  }
}
```

Поддерживаемые действия:

- `on`;
- `off`;
- `restart`.

`seq` монотонно увеличивается для конкретного устройства. Агент не должен повторно применять sequence, который уже записан в локальном state.

## POST `/v1/devices/{device_id}/command-result`

Подтверждает применение команды.

### Авторизация

```http
Authorization: Bearer DEVICE_API_TOKEN
```

### Запрос

```json
{
  "seq": 12,
  "ok": true,
  "message": "FRPC запущен, PID 1234"
}
```

### Ответ

```json
{
  "ok": true
}
```

Результат принимается только если `seq` совпадает с текущим `command_seq`. Устаревший result игнорируется.

## Общие ответы ошибок

```json
{
  "ok": false,
  "error": "description"
}
```

Статусы:

- `400` — некорректный JSON или payload;
- `401` — отсутствующий/неверный device token или revoked device;
- `404` — неизвестный endpoint;
- `500` — необработанная серверная ошибка.

## Совместимость

Изменения внутри существующего `/v1` должны оставаться обратно совместимыми. Несовместимый контракт требует нового API prefix (`/v2`) и миграционного плана для уже установленных агентов.

## Требования к новым полям telemetry

- сервер должен терпимо относиться к отсутствующему полю;
- Telegram UI должен иметь безопасное значение по умолчанию;
- старый agent и новый server должны продолжать работать вместе;
- новый agent не должен требовать немедленного обновления всех серверов без проверки версии `/healthz`.
