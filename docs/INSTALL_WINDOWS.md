# Установка Windows-клиента

## Требования

- Windows 10/11 Pro, Enterprise или Education x64 либо поддерживаемая Windows Server;
- PowerShell 5.1+;
- права локального администратора;
- Microsoft OpenSSH Client;
- доступ к Hermes server на API и tunnel ports.

Windows Home не поддерживает входящие RDP-сессии штатными средствами.

Windows 10 x64 поддерживается и из 32-битного Windows PowerShell: installer использует native system path/Sysnative для Microsoft OpenSSH, когда это необходимо.

## Fresh pairing нового ПК

1. В Telegram отправьте `/start`.
2. Нажмите **➕ ДОБАВИТЬ ПК**.
3. Откройте PowerShell от имени администратора.
4. Скопируйте команду из Telegram целиком.
5. Введите название компьютера.

Pairing-код одноразовый и ограничен по времени. Если он истёк или уже использован, нажмите **🔁 НОВЫЙ КОД** и используйте обновлённую команду.

Fresh installer создаёт новую device registration и локальную Ed25519 identity только для нового клиента. Private key остаётся на Windows; сервер получает только public key.

## Успешный результат fresh install

```text
=== ГОТОВО ===
Компьютер: office-pc
RDP: SERVER:53389
Туннель: OpenSSH
Задача: Hermes RDP Agent
```

## Уже установлен Hermes: используйте Repair

Если ПК уже зарегистрирован в Telegram и локальная identity сохранена, не запускайте новый fresh pairing. В карточке существующего устройства нажмите **🛠 ВОССТАНОВИТЬ КЛИЕНТ**.

Repair сохраняет:

- Device ID и API-token;
- Ed25519 keypair;
- `known_hosts`;
- назначенный RDP-порт.

Repair может восстановить Hermes Agent и Scheduled Task существующего устройства. Он привязан к выбранному Device ID и не создаёт вторую device registration.

Успех подтверждается строкой:

```text
REPAIR=PASS
```

Если потеряны `device.json`, private key или `known_hosts`, обычный Repair намеренно останавливается. Автоматический re-pair/rekey в этот flow не входит.

## Обновление существующего клиента

`scripts/update-client.ps1` предназначен для здоровой существующей установки. Он проверяет baseline, подготавливает candidate до runtime mutation, сохраняет previous agent/task snapshot, не переписывает identity/config/trust material и при failure после mutation выполняет automatic rollback.

Если baseline уже повреждён, используйте Repair, а не fresh pairing.

## Проверка

Проверьте Scheduled Task, Hermes log и наличие одного Hermes SSH transport. Затем выполните внешний Microsoft Remote Desktop test через назначенный endpoint.

## Безопасность

Не публикуйте pairing-коды, API-token или private key. Hermes не требует ослабления Microsoft Defender для штатной установки, update или repair.
