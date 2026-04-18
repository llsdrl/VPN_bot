# WireGuard VPN - Complete Setup Guide

## Пошаговая инструкция

### Этап 1: Подготовка сервера
1. Арендуйте VPS с Ubuntu 22.04 LTS
2. Подключитесь по SSH
3. Обновите систему: `apt update && apt upgrade -y`

### Этап 2: Установка WireGuard SERVER
```bash
# Скачайте скрипт на сервер
scp wireguard-configs/01-server-install.sh root@YOUR_SERVER:/tmp/
ssh root@YOUR_SERVER

# Запустите
chmod +x /tmp/01-server-install.sh
/tmp/01-server-install.sh
```

Скрипт автоматически:
- Устанавливает WireGuard
- Генерирует ключи сервера
- Создаёт конфигурацию wg0.conf
- Настраивает UFW (порт 51820/UDP)
- Включает IP forwarding
- Запускает службу

### Этап 3: Добавление клиентов
```bash
# Скачайте скрипт управления клиентами
scp wireguard-configs/02-add-client.sh root@YOUR_SERVER:/tmp/

# Добавьте клиентов
chmod +x /tmp/02-add-client.sh
/tmp/02-add-client.sh android
/tmp/02-add-client.sh ios
/tmp/02-add-client.sh windows
```

### Этап 4: Защита (опционально)
```bash
chmod +x /tmp/03-security-hardening.sh
/tmp/03-security-hardening.sh
```

### Этап 5: Подключение клиентов

**Android/iOS:**
- Установите WireGuard из Google Play/App Store
- Импортируйте конфигурацию или сканируйте QR-код
- Включите VPN

**Windows:**
- Скачайте WireGuard: https://www.wireguard.com/install/
- Импортируйте конфигурацию .conf
- Включите VPN

## Команды проверки статуса

```bash
# Статус WireGuard
sudo wg

# Статус сервиса
sudo systemctl status wg-quick@wg0

# Активные подключения
sudo wg show

# Проверка работы
ping -c 3 10.0.0.1
```

## Управление службой

```bash
# Перезапуск
sudo systemctl restart wg-quick@wg0

# Остановка
sudo systemctl stop wg-quick@wg0

# Автозагрузка (уже включена)
sudo systemctl enable wg-quick@wg0
```

## Удаление клиента

```bash
# Отредактируйте вручную
sudo nano /etc/wireguard/wg0.conf

# Удалите блок [Peer] нужного клиента
# Перезапустите
sudo systemctl restart wg-quick@wg0
```

##Notes

- Server Private Key = генерируется при установке
- Client configs сохраняются в `/etc/wireguard/clients/`
- QR-коды: `qrencode -t png -o /tmp/android.png < /etc/wireguard/clients/android.conf`