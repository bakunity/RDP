# Установка Windows-клиента

## Требования

- Windows 10/11 Pro, Enterprise или Education x64;
- PowerShell 5.1+;
- права локального администратора;
- встроенный OpenSSH Client или возможность установить Windows Capability;
- доступ к серверу на `7000/tcp` и `7443/tcp`.

Windows Home не поддерживает входящие RDP-сессии штатными средствами.

## Установка

1. В Telegram отправьте `/start`.
2. Нажмите **➕ ДОБАВИТЬ ПК**.
3. Откройте PowerShell от имени администратора.
4. Скопируйте команду из Telegram целиком.
5. Введите название компьютера.

Не публикуйте pairing-код и fingerprint. Pairing-код одноразовый и ограничен по времени.

## Что делает установщик

- проверяет редакцию и архитектуру Windows;
- находит или устанавливает OpenSSH Client;
- останавливает старые Hermes/FRP задачи;
- сохраняет legacy-установку отдельно;
- создаёт Ed25519 keypair локально;
- отправляет серверу только public key;
- проверяет HTTPS certificate fingerprint;
- получает и закрепляет SSH host key;
- включает RDP и Windows Firewall rules;
- создаёт `Hermes RDP Agent` от имени `SYSTEM`;
- запускает reverse SSH-туннель.

## Успешный результат

```text
=== ГОТОВО ===
Компьютер: office-pc
RDP: SERVER:53389
Туннель: OpenSSH
Задача: Hermes RDP Agent
```

## Проверка

```powershell
Get-ScheduledTask -TaskName 'Hermes RDP Agent'
Get-Process ssh -ErrorAction SilentlyContinue
Get-Content 'C:\ProgramData\HermesRDP\agent.log' -Tail 50
```

На сервере назначенный порт должен начать слушаться только после запуска `ssh.exe`.

## Повторная установка поверх старой версии

Legacy-каталог переносится в:

```text
C:\ProgramData\HermesRDP-legacy-YYYYMMDD-HHMMSS
```

Установщик не должен читать защищённые старые private keys пофайлово. При устаревших ACL допускается ограниченный `takeown`/`icacls` только для каталога Hermes RDP.

Не удаляйте legacy backup до успешного внешнего RDP-теста и проверки перезагрузки.

## Проверка из другой сети

Подключитесь стандартным Microsoft Remote Desktop с телефона или другого компьютера через отдельный интернет-канал:

```text
SERVER_IP_OR_DOMAIN:53389
```

Так подтверждается полный путь до Windows, а не только локальная доступность сервера.
