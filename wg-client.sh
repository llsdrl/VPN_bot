#!/bin/bash

set -e

CLIENTS_DIR="/etc/wireguard/clients"
CONFIG_DIR="/etc/wireguard"

add_client() {
    local client_name="$1"
    local client_ip="$2"
    
    mkdir -p "${CLIENTS_DIR}"
    
    cd "${CONFIG_DIR}"
    wg genkey | tee "${CLIENTS_DIR}/${client_name}.priv" | wg pubkey > "${CLIENTS_DIR}/${client_name}.pub"
    
    local client_private=$(cat "${CLIENTS_DIR}/${client_name}.priv")
    local client_public=$(cat "${CLIENTS_DIR}/${client_name}.pub")
    local server_public=$(cat server_public.key)
    
    cat > "${CLIENTS_DIR}/${client_name}.conf" << EOF
[Interface]
PrivateKey = ${client_private}
Address = ${client_ip}/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = ${server_public}
Endpoint = YOUR_SERVER_IP_OR_DOMAIN:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
EOF

    echo "${client_public}    ${client_ip}" >> peers.conf
    
    wg addpeer wg0 < "${CLIENTS_DIR}/${client_name}.pub" 2>/dev/null || \
        echo -e "\n[Peer]\nPublicKey = ${client_public}\nAllowedIPs = ${client_ip}/32" >> /etc/wireguard/wg0.conf
    
    qrencode -t ansiutf8 < "${CLIENTS_DIR}/${client_name}.conf"
    
    echo "Client created: ${client_name}"
    echo "Config: ${CLIENTS_DIR}/${client_name}.conf"
    echo "Public Key: ${client_public}"
}

remove_client() {
    local client_name="$1"
    
    local client_pub=$(cat "${CLIENTS_DIR}/${client_name}.pub" 2>/dev/null)
    
    if [ -n "$client_pub" ]; then
        wg set wg0 peer "$client_pub" remove 2>/dev/null || true
    fi
    
    sed -i "/${client_name}/d" /etc/wireguard/wg0.conf
    rm -f "${CLIENTS_DIR}/${client_name}.conf" \
          "${CLIENTS_DIR}/${client_name}.priv" \
          "${CLIENTS_DIR}/${client_name}.pub"
    
    echo "Client removed: ${client_name}"
}

list_clients() {
    echo "=== Active Peers ==="
    wg show wg0 peers
    
    echo ""
    echo "=== Client Files ==="
    ls -la "${CLIENTS_DIR}/" 2>/dev/null || echo "No clients yet"
}

case "$1" in
    add)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 add <client_name> <client_ip>"
            echo "Example: $0 add android 10.0.0.2"
            exit 1
        fi
        add_client "$2" "$3"
        ;;
    remove)
        if [ -z "$2" ]; then
            echo "Usage: $0 remove <client_name>"
            exit 1
        fi
        remove_client "$2"
        ;;
    list)
        list_clients
        ;;
    *)
        echo "Usage: $0 {add|remove|list}"
        echo "  add <name> <ip>   - Add new client"
        echo "  remove <name>     - Remove client"
        echo "  list              - List clients"
        exit 1
        ;;
esac