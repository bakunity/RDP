# Установка Windows-клиента

## Требования

- Windows Pro, Enterprise или Education;
- PowerShell от администратора;
- доступ к GitHub, Hermes API и FRP control port.

## Через Telegram

1. Нажми `➕ ДОБАВИТЬ ПК`.
2. Скопируй готовую команду.
3. Запусти её в PowerShell от администратора.
4. Введи понятное название компьютера.

Установщик сам:

- проверит редакцию Windows;
- скачает FRP и проверит SHA-256;
- зарегистрирует устройство;
- включит RDP и штатное правило Windows Firewall;
- установит агент и Scheduled Task;
- покажет постоянный внешний адрес.

## Файлы

```text
C:\ProgramData\HermesRDP├── frpc.exe
├── frpc.toml
├── frp-ca.crt
├── HermesRdpAgent.ps1
├── device.json
├── agent-state.json
└── agent.log
```

## Удаление

Сначала удали устройство в Telegram, затем на Windows:

```powershell
$u='https://raw.githubusercontent.com/bakunity/RDP/main/scripts/uninstall-client.ps1'
& ([scriptblock]::Create((irm $u)))
```
