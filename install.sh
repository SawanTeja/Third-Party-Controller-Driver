#!/usr/bin/env bash
# install.sh - Universal Installer for Cosmic Byte & ShanWan Linux Driver

set -e

if [ "$EUID" -ne 0 ]; then
    echo "[-] Please run as root: sudo ./install.sh"
    exit 1
fi

echo "========================================================="
echo "  Installing Cosmic Byte & ShanWan Linux Xbox Driver     "
echo "========================================================="

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/5] Compiling driver..."
make -C "$DIR" clean
make -C "$DIR"

echo "[2/5] Installing binary to /usr/local/bin/cosmic-xbox-driver..."
install -m 755 "$DIR/cosmic-xbox-driver" /usr/local/bin/cosmic-xbox-driver

echo "[3/5] Installing udev rules..."
install -m 644 "$DIR/99-cosmic-xbox.rules" /etc/udev/rules.d/99-cosmic-xbox.rules
udevadm control --reload-rules
udevadm trigger

echo "[4/5] Loading uinput kernel module..."
modprobe uinput || true
if ! grep -q "uinput" /etc/modules-load.d/uinput.conf 2>/dev/null; then
    echo "uinput" > /etc/modules-load.d/uinput.conf
fi

echo "[5/5] Installing and starting systemd service..."
install -m 644 "$DIR/cosmic-xbox-driver.service" /etc/systemd/system/cosmic-xbox-driver.service
systemctl daemon-reload
systemctl enable --now cosmic-xbox-driver.service

echo ""
echo "========================================================="
echo "  Installation Successful!                               "
echo "========================================================="
echo "  Status:"
systemctl status cosmic-xbox-driver.service --no-pager -l | head -n 12
echo ""
echo "  Your controller is now active as a genuine Xbox 360 controller"
echo "  with FULL ANALOG TRIGGERS (L2 & R2) and VIBRATION enabled!"
echo "========================================================="
