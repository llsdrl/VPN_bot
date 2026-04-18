#!/bin/bash
set -e

echo "=== WireGuard Security Hardening ==="

echo "[1/7] Disabling IPv6 if not needed (optional)..."
# sysctl -w net.ipv6.conf.all.disable_ipv6=1
# sysctl -w net.ipv6.conf.default.disable_ipv6=1

echo "[2/7] Configuring UFW rate limiting..."
ufw limit 51820/udp

echo "[3/7] Installing fail2ban..."
apt install -y fail2ban

cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/fail2ban.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

echo "[4/7] Disabling WireGuard logging..."
# Note: WireGuard doesn't have built-in logging disable option
# But we can limit systemd logging
systemctl mask systemd-journald.service || true

# Instead, limit journal size
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/10-vpn.conf <<EOF
[Journal]
SystemMaxUse = 50M
RuntimeMaxUse = 50M
SystemKeepFree = 100M
RuntimeKeepFree = 100M
MaxRetentionSec = 1week
ForwardToSyslog = no
ForwardToWall = no
EOF

echo "[5/7] Configuring kernel hardening..."
cat >> /etc/sysctl.conf <<EOF

# Kernel hardening
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 2
EOF

sysctl -p

echo "[6/7] Disabling ICMP redirect acceptance..."
sysctl -w net.ipv4.conf.all.accept_redirects=0
sysctl -w net.ipv4.conf.default.accept_redirects=0
sysctl -w net.ipv6.conf.all.accept_redirects=0
sysctl -w net.ipv6.conf.default.accept_redirects=0

echo "[7/7] Enabling DDOS protection (syncookies)..."
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_syn_retries=2
sysctl -w net.ipv4.tcp_synack_retries=2

# Apply permanently
echo "net.ipv4.tcp_syncookies=1" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.accept_redirects=0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_redirects=0" >> /etc/sysctl.conf

echo ""
echo "=== Security Hardening Complete ==="