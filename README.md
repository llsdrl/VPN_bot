# WireGuard VPN - Полное руководство по развертыванию

---

## 1. ПОШАГОВАЯ ИНСТРУКЦИЯ

### Требования к серверу:
- Ubuntu 22.04 LTS (или новее)
- Публичный IP-адрес или домен
- Root-доступ

### Шаг 1: Подготовка сервера
```bash
# Обновление системы
apt update && apt upgrade -y
```

### Шаг 2: Установка WireGuard
```bash
apt install -y wireguard wireguard-tools qrencode
```

### Шаг 3: Генерация ключей
```bash
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key
```

### Шаг 4: Настройка UFW (брандмауэр)
```bash
# Установка UFW
apt install -y ufw

# Открытие портов
ufw allow 51820/udp   # WireGuard
ufw allow 22/tcp      # SSH (оставьте если нужен удаленный доступ)

# Безопасность по умолчанию
ufw default deny incoming
ufw default allow outgoing

# Включение
ufw enable
```

### Шаг 5: Настройка IP forwarding
```bash
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
```

### Шаг 6: Запуск WireGuard
```bash
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
systemctl status wg-quick@wg0
```

---

## 2. АВТОМАТИЧЕСКИЙ СКРИПТ УСТАНОВКИ

См. файл: `install-wireguard.sh`

**Использование:**
```bash
chmod +x install-wireguard.sh
./install-wireguard.sh
```

---

## 3. УПРАВЛЕНИЕ КЛИЕНТАМИ

См. файл: `wg-client.sh`

**Команды:**
```bash
# Добавить клиента
./wg-client.sh add android 10.0.0.2
./wg-client.sh add ios 10.0.0.3

# Удалить клиента
./wg-client.sh remove android

# Список клиентов
./wg-client.sh list
```

---

## 4. КОНФИГУРАЦИЯ СЕРВЕРА

См. файл: `server-wg0.conf` (расположение: `/etc/wireguard/wg0.conf`)

```ini
[Interface]
PrivateKey = <server_private_key>
Address = 10.0.0.1/24
ListenPort = 51820

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -A FORWARD -o wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -o wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <client_public_key>
AllowedIPs = 10.0.0.2/32
```

---

## 5. КОНФИГУРАЦИЯ КЛИЕНТОВ

См. файл: `client-configs.conf`

### Android/iOS (QR-код):
```bash
qrencode -t ansiutf8 < client.conf
```

### Windows:
Импортировать `.conf` файл в приложение WireGuard.

---

## 6. ПРОВЕРКА СТАТУСА

### Проверить статус WireGuard:
```bash
wg show
```

### Проверить активные подключения:
```bash
wg show wg0
```

### Проверить статус сервиса:
```bash
systemctl status wg-quick@wg0
```

### Проверить правила iptables:
```bash
iptables -L -v -n
```

### Проверить UFW:
```bash
ufw status verbose
```

---

## 7. БЕЗОПАСНОСТЬ

### Защита от брутфорса (fail2ban):
```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Защита от сканирования портов:
```bash
# Ограничение попыток подключения
iptables -A INPUT -p udp --dport 51820 -m state --state NEW -m recent --set
iptables -A INPUT -p udp --dport 51820 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
```

### Отключение логирования (частично):
```bash
# В wg0.conf добавьте (ограниченная функциональность):
# WireGuard не логирует трафик по умолчанию
# Для отключения логов системы:
systemctl mask rsyslog.service
```

### Дополнительные меры:
```bash
# Отключить IPv6 если не используется
echo "net.ipv6.conf.all.disable_ipv6=1" >> /etc/sysctl.conf
sysctl -p

# Ограничить ICMP
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp -j DROP
```

### Обновление WireGuard:
```bash
apt update && apt upgrade -y wireguard wireguard-tools
```

---

## 8. УДАЛЕНИЕ VPN

```bash
systemctl stop wg-quick@wg0
systemctl disable wg-quick@wg0
rm /etc/wireguard/wg0.conf
ufw delete allow 51820/udp
```

---

## 9. ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Перезапуск VPN
systemctl restart wg-quick@wg0

# Добавить нового клиента вручную
wg set wg0 peer <PUBLIC_KEY> allowed-ips 10.0.0.5/32

# Удалить клиента
wg set wg0 peer <PUBLIC_KEY> remove

# Просмотр всех пиров
wg show wg0 peers

# Тестирование подключения
ping 10.0.0.1
```

---

## 10. ПРИМЕЧАНИЯ

- **Публичный IP**: Замените `YOUR_PUBLIC_IP_OR_DOMAIN` на ваш реальный IP или домен
- **DNS**: Используйте 1.1.1.1 (Cloudflare) или 8.8.8.8 (Google)
- **AllowedIPs = 0.0.0.0/0** - весь трафик через VPN
- Для split-tunnel укажите конкретные подсети