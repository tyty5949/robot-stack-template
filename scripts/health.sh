#!/usr/bin/env bash
set -euo pipefail
echo "== System =="
uptime
echo "== Disk =="
df -h /
echo "== Mosquitto =="
systemctl is-active mosquitto || (echo 'mosquitto is not active' && exit 1)
echo "== Recent logs =="
journalctl -u mosquitto -n 50 --no-pager || true
