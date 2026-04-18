#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <client-name>"
    echo "Example: $0 iphone"
    exit 1
fi

CLIENT_NAME=$1
SERVER_CONFIG=/etc/wireguard/wg0.conf

echo "=== Adding WireGuard Client: $CLIENT_NAME ==="

echo "[1/5] Generating client keys..."
CLIENT_PRIVATE_KEY=$(wg genkey)
CLIENT_PUBLIC_KEY=$(echo "$CLIENT_PRIVATE_KEY" | wg pubkey)
CLIENT_PRESHARED_KEY=$(wg genpsk)

echo "[2/5] Determining server details..."
SERVER_PUB_KEY=$(grep "PrivateKey" /etc/wireguard/wg0.conf | awk '{print $3}' | wg pubkey)
SERVER_PORT=$(grep "ListenPort" /etc/wireguard/wg0.conf | awk '{print $3}')
SERVER_IP=$(curl -s ifconfig.me)

echo "[3/5] Assigning IP address..."
USED_IPS=$(grep "AllowedIPs" /etc/wireguard/wg0.conf | grep -v "^#" | awk '{print $3}' | cut -d'/' -f1 | sort -t. -k1,1n -k2,2n -k3,3n -k4,4n)
LAST_IP=$(echo "$USED_IPS" | tail -1 | cut -d. -f4)
CLIENT_IP="10.0.0.$((LAST_IP + 1))"

echo "[4/5] Adding peer to server config..."
cat >> /etc/wireguard/wg0.conf <<EOF

[Peer]
PublicKey = $CLIENT_PUBLIC_KEY
PresharedKey = $CLIENT_PRESHARED_KEY
AllowedIPs = $CLIENT_IP/32
PersistentKeepalive = 25
EOF

echo "[5/5] Restarting WireGuard..."
wg syncconf wg0 <(cat $SERVER_CONFIG)

echo "[6/5] Generating client config file..."
mkdir -p /etc/wireguard/clients
cat > /etc/wireguard/clients/${CLIENT_NAME}.conf <<EOF
[Interface]
PrivateKey = $CLIENT_PRIVATE_KEY
Address = $CLIENT_IP/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SERVER_PUB_KEY
PresharedKey = $CLIENT_PRESHARED_KEY
Endpoint = $SERVER_IP:$SERVER_PORT
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
EOF

echo ""
echo "=== Client Added Successfully ==="
echo "Client Name: $CLIENT_NAME"
echo "Client IP: $CLIENT_IP"
echo "Config File: /etc/wireguard/clients/${CLIENT_NAME}.conf"
echo ""
echo "Show config with: sudo cat /etc/wireguard/clients/${CLIENT_NAME}.conf"