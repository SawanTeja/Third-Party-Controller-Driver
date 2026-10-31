# Third-Party Controller Driver for Linux

A lightweight Linux driver for **Cosmic Byte Blitz**, **ShanWan**, and generic third-party gamepads. It connects the controller as an authentic **Xbox 360 controller** with working vibration and full analog trigger sensitivity.

---
## Tested 

<img width="1189" height="839" alt="image" src="https://github.com/user-attachments/assets/6a8e8d19-669e-48d5-9449-725cf6f2c25c" />



https://github.com/user-attachments/assets/084ffcd3-41cf-4784-877a-147775d4d87e

The controller i have tested in the video is Cosmic Byte Blitz on Ubuntu


---

## Features

- **Genuine Xbox 360 Emulation**: Detected natively as an Xbox 360 pad by Steam, Wine/Proton, emulators, and browsers.
- **Working Vibration**: Translates in-game force feedback rumble directly to controller motors.
- **True Analog Triggers**: Full L2/R2 sensitivity (0–255) for racing and shooter games (not digital on/off).
- **Correct Layout**: Standard Xbox A, B, X, Y button layout out of the box.
- **Background Service**: Runs automatically at boot as a systemd service with zero configuration.

---

## Prerequisites

Ensure your system has the standard C compiler and build tools installed:

- **Ubuntu / Debian / Linux Mint / Pop!_OS**:
  ```bash
  sudo apt update && sudo apt install -y build-essential
  ```
- **Fedora / RHEL**:
  ```bash
  sudo dnf install -y gcc glibc-devel make
  ```
- **Arch Linux / Manjaro**:
  ```bash
  sudo pacman -S --needed base-devel
  ```
- **openSUSE**:
  ```bash
  sudo zypper install -t pattern devel_basis
  ```

*(Note: `install.sh` will also attempt to auto-install these if they are missing on supported distributions).*

---

## Installation

Run the automated installer:

```bash
git clone https://github.com/SawanTeja/Third-Party-Controller-Driver.git ControllerDriver
cd ControllerDriver
sudo ./install.sh
```

---

## Testing

- **Check Service**:
  ```bash
  systemctl status cosmic-xbox-driver.service
  ```
- **Test Analog Triggers**:
  ```bash
  python3 monitor_triggers.py
  ```
- **Test Vibration**:
  ```bash
  python3 test_rumble.py
  ```
- **Browser Test**: Open [gamepad-tester.com](https://gamepad-tester.com/) to verify all buttons, analog triggers, and rumble.

---

## Uninstallation

To remove the driver:

```bash
sudo ./uninstall.sh
```

---

## Configuration

The driver works out of the box with zero configuration. If your controller requires custom adjustments (e.g. disabling vibration or swapping triggers), edit `/etc/cosmic-xbox-driver.conf`:

```ini
# /etc/cosmic-xbox-driver.conf

# Turn OFF all vibration/rumble (useful if trigger pulls cause violent or unwanted vibration)
disable_rumble = false

# Swap L2 (LT) and R2 (RT) triggers if your clone has them reversed
swap_triggers = false
```

Apply changes:
```bash
sudo systemctl restart cosmic-xbox-driver.service
```

---

## Supported Controllers

- **Cosmic Byte Blitz** (2.4GHz Wireless Dongle `20bc:5001` & Wired `05ac:033e`)
- **Redragon Gamepads** (Wired `2563:0599` & Wireless 2.4GHz Dongle `2563:0526`)
- **ShanWan / ShenZhen Technology Gamepads** (`2563:0526`, `2563:0575`, `2563:0523`, `20bc:5001`)
- **DragonRise / Generic Clone Gamepads** (Vendor `0x0079`)
- Generic third-party PC/Android controllers using ShanWan chipsets
