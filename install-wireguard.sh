#!/bin/bash

set -e

echo "=== WireGuard VPN Installation Script ==="
echo "Server OS: Ubuntu 22.04+"

SERVER_WG_IP="10.0.0.1"
SERVER_PORT="51820"
ALLOWED_IPS="0.0.0.0/0, ::/0"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

echo "[1/7] Updating system..."
apt update && apt upgrade -y

echo "[2/7] Installing WireGuard..."
apt install -y wireguard wireguard-tools linux-headers-$(uname -r) qrencode

echo "[3/7] Generating server keys..."
cd /etc/wireguard
wg genkey | tee server_private.key | wg pubkey > server_public.key

SERVER_PRIVATE_KEY=$(cat server_private.key)
SERVER_PUBLIC_KEY=$(cat server_public.key)

echo "[4/7] Creating server configuration..."
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = ${SERVER_PRIVATE_KEY}
Address = ${SERVER_WG_IP}/24
ListenPort = ${SERVER_PORT}
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Client: android
[Peer]
PublicKey = CLIENT_PUBLIC_KEY_HERE
AllowedIPs = 10.0.0.2/32
PersistentKeepalive = 25
EOF

chmod 600 /etc/wireguard/wg0.conf

echo "[5/7] Configuring UFW firewall..."
apt install -y ufw

ufw allow ${SERVER_PORT}/udp
ufw allow OpenSSH
ufw default deny incoming
ufw default allow outgoing

cat >> /etc/ufw/before.rules << 'EOF'
*nat
:POSTROUTING ACCEPT [0:0]
-A POSTROUTING -s 10.0.0.0/24 ! -d 10.0.0.0/24 -o eth0 -j MASQUERADE
COMMIT
EOF

echo "Enable IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

ufw enable

echo "[6/7] Enabling and starting WireGuard service..."
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
systemctl status wg-quick@wg0 --no-pager

echo "[7/7] Server setup complete!"
echo ""
echo "=== Server Info ==="
echo "Public Key: ${SERVER_PUBLIC_KEY}"
echo "Server IP: ${SERVER_WG_IP}"
echo "Listen Port: ${SERVER_PORT}"
echo ""
echo "Save this public key for client configurations: ${SERVER_PUBLIC_KEY}"