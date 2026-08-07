# Control-state live validation

Фактически подтверждено на тестовой инфраструктуре до этого патча:

- `OFF` разрывает активную RDP-сессию и закрывает endpoint;
- `ON` восстанавливает endpoint и повторное RDP-подключение;
- Windows 10 Pro x64 успешно работает через system OpenSSH;
- после перезагрузки Windows 10 Scheduled Task автоматически восстанавливает tunnel и RDP endpoint;
- найден compatibility defect: 32-bit Windows PowerShell на x64 Windows видит native OpenSSH через `Sysnative`, а старый installer проверял только redirectable `System32`.

Патч не меняет транспортный протокол. Он исправляет определение SSH-процесса, отображение desired/actual state, command-result UX и native OpenSSH path resolution.
