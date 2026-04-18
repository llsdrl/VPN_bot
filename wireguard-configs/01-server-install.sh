#!/bin/bash
set -e

SERVER_PUB_IP=$(curl -s ifconfig.me)
SERVER_PRIVATE_KEY=""
SERVER_PUBLIC_KEY=""
SERVER_PORT=51820

echo "=== WireGuard VPN Auto Installer ==="
echo "Server IP: $SERVER_PUB_IP"

echo "[1/7] Updating system..."
apt update && apt upgrade -y

echo "[2/7] Installing WireGuard..."
apt install -y wireguard wireguard-tools ufw

echo "[3/7] Generating server keys..."
SERVER_PRIVATE_KEY=$(wg genkey)
SERVER_PUBLIC_KEY=$(echo "$SERVER_PRIVATE_KEY" | wg pubkey)

echo "[4/7] Creating server config..."
mkdir -p /etc/wireguard

cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = $SERVER_PORT
SaveConfig = false

# PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
# PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; ip6tables -A FORWARD -i wg0 -j ACCEPT; ip6tables -A FORWARD -o wg0 -j ACCEPT; ip6tables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; ip6tables -D FORWARD -i wg0 -j ACCEPT; ip6tables -D FORWARD -o wg0 -j ACCEPT; ip6tables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

EOF

chmod 600 /etc/wireguard/wg0.conf

echo "[5/7] Configuring UFW firewall..."
ufw --force disable
ufw default deny incoming
ufw default allow outgoing
ufw allow $SERVER_PORT/udp
ufw allow OpenSSH
ufw --force enable

echo "[6/7] Enabling IP forwarding..."
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sysctl -p

echo "[7/7] Starting WireGuard service..."
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
systemctl status wg-quick@wg0 --no-pager

echo ""
echo "=== Installation Complete ==="
echo "Server Public Key: $SERVER_PUBLIC_KEY"
echo "Server IP: $SERVER_PUB_IP"
echo "Listen Port: $SERVER_PORT"
echo ""
echo "Use ./02-add-client.sh to add new clients"