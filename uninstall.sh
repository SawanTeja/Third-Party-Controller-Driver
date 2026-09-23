#!/usr/bin/env bash
# uninstall.sh - Clean Uninstaller for Cosmic Byte & ShanWan Linux Driver

set -e

if [ "$EUID" -ne 0 ]; then
    echo "[-] Please run as root: sudo ./uninstall.sh"
    exit 1
fi

echo "Stopping and disabling cosmic-xbox-driver service..."
systemctl stop cosmic-xbox-driver.service || true
systemctl disable cosmic-xbox-driver.service || true

echo "Removing files..."
rm -f /etc/systemd/system/cosmic-xbox-driver.service
rm -f /etc/udev/rules.d/99-cosmic-xbox.rules
rm -f /usr/local/bin/cosmic-xbox-driver

udevadm control --reload-rules
systemctl daemon-reload

echo "Uninstallation complete. Cleaned up all driver files."
