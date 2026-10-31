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

check_and_install_dependencies() {
    local need_deps=0

    if ! command -v make >/dev/null 2>&1; then
        need_deps=1
    fi

    if ! command -v gcc >/dev/null 2>&1 && ! command -v cc >/dev/null 2>&1; then
        need_deps=1
    fi

    if [ "$need_deps" -eq 0 ]; then
        local compiler
        compiler=$(command -v gcc || command -v cc)
        if ! printf '#include <stdio.h>\nint main(void){return 0;}\n' | "$compiler" -x c - -o /tmp/.test_compile 2>/dev/null; then
            need_deps=1
        fi
        rm -f /tmp/.test_compile
    fi

    if [ "$need_deps" -ne 0 ]; then
        echo "[*] Missing build tools or C library headers (stdio.h)."
        echo "    Installing required build dependencies..."
        if command -v apt-get >/dev/null 2>&1; then
            echo "    -> Detected Debian/Ubuntu. Installing 'build-essential'..."
            apt-get update -y && apt-get install -y build-essential
        elif command -v dnf >/dev/null 2>&1; then
            echo "    -> Detected Fedora/RHEL. Installing 'gcc glibc-devel make'..."
            dnf install -y gcc glibc-devel make
        elif command -v pacman >/dev/null 2>&1; then
            echo "    -> Detected Arch Linux. Installing 'base-devel'..."
            pacman -Sy --noconfirm --needed base-devel
        elif command -v zypper >/dev/null 2>&1; then
            echo "    -> Detected openSUSE. Installing 'devel_basis'..."
            zypper install -y -t pattern devel_basis
        else
            echo "[-] Error: C compiler and standard headers (e.g. build-essential / libc-dev) are missing."
            echo "    Please install them manually using your distribution's package manager and re-run."
            exit 1
        fi
    fi
}

echo "[1/5] Checking dependencies and compiling driver..."
check_and_install_dependencies
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
if [ ! -f /etc/cosmic-xbox-driver.conf ]; then
    install -m 644 "$DIR/cosmic-xbox-driver.conf.example" /etc/cosmic-xbox-driver.conf
    echo "      Created default config at /etc/cosmic-xbox-driver.conf"
fi
install -m 644 "$DIR/cosmic-xbox-driver.service" /etc/systemd/system/cosmic-xbox-driver.service
systemctl daemon-reload
systemctl restart cosmic-xbox-driver.service
systemctl enable cosmic-xbox-driver.service

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
