#!/bin/bash
# FK Agent OS — GCP e2-micro hardening. Run ONCE after VM creation (as root).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y install ufw fail2ban curl
timedatectl set-timezone Asia/Kolkata
systemctl enable systemd-timesyncd 2>/dev/null || true
# 2GB swap (e2-micro has 1GB RAM — swap is the safety net)
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  sysctl -w vm.swappiness=10
fi
# SSH: keys only, no root login
sed -ri 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -ri 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh
# UFW: only SSH + web
ufw default deny incoming
ufw default allow outgoing
ufw --force enable
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
systemctl enable --now fail2ban
# unattended security patches
apt-get -y install unattended-upgrades
dpkg-reconfigure -f noninteractive unattended-upgrades 2>/dev/null || true
mkdir -p /var/log/fk /opt/secrets
chmod 700 /opt/secrets
echo "harden done $(date -u +%FT%TZ) | swap: $(free -h | awk '/Swap/{print $2}')"
