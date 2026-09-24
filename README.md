# Cosmic Byte & ShanWan Linux Xbox Driver

A high-performance, native Linux driver and virtual Xbox 360 controller bridge for **Cosmic Byte Blitz** and generic **ShenZhen ShanWan Technology** gamepads (Vendor IDs: `20bc:5001`, `2563:0575`, `2563:0523`, etc.).

---

## Why This Driver Exists (The Problem With Existing Workarounds)

Most guides and temporary fixes for Cosmic Byte Blitz / ShanWan controllers on Linux recommend setting the kernel parameter `usbcore.old_scheme_first=1`. While this causes the device to enumerate as a Nintendo Switch Pro Controller (`057e:2009`), it introduces severe problems:

1. **Destroys Analog Trigger Sensitivity**: Nintendo Switch Pro controllers physically only have digital buttons (ZL/ZR). The Linux `hid-nintendo` driver completely throws away analog trigger data, turning **R2 and L2 into binary on/off buttons**. In racing games and shooters, you cannot control throttle, brake, or half-pulls.
2. **Inverted ABXY Layout**: Nintendo uses the Japanese layout (A is East, B is South, X is North, Y is West). This inverts the physical button markings on your Xbox-styled controller, requiring remapping tools like `input-remapper`.
3. **Browser & Game Incompatibilities**: The raw HID Switch handshake blocks web-based gamepad testers (`gamepad-tester.com`) and requires custom udev rules.
4. **Fragile System Changes**: Modifying GRUB kernel parameters requires reboots and can interfere with other USB devices.

---

## The Solution: Reverse Engineering Native Mode

By reverse-engineering the native ShanWan USB communication (`20bc:5001`):

- **True Analog Triggers**: In its native mode, the controller hardware reports full 8-bit analog axes (`ABS_BRAKE` for L2 and `ABS_GAS` for R2) with values from **0 to 255**.
- **Hardware Rumble**: Force-feedback rumble packets can be sent directly to the controller's HID interface (`/dev/hidraw*`) using the ShanWan dual-motor protocol.
- **Genuine Xbox 360 Emulation**: Using Linux `/dev/uinput`, this driver creates an authentic **Microsoft X-Box 360 pad (`045e:028e`)**:
  - Full analog sensitivity on LT (`ABS_Z`) and RT (`ABS_RZ`) (0–255).
  - Standard Xbox button layout (`BTN_A`, `BTN_B`, `BTN_X`, `BTN_Y`, `LB`, `RB`, `Start`, `Back`, `Guide`, `L3`, `R3`).
  - Native force-feedback rumble forwarded from games to physical motors.
  - Exclusive device grabbing (`EVIOCGRAB`) so games and Steam only see the virtual Xbox 360 controller (zero duplicate inputs).
  - Plug-and-play compatibility with **Steam (Big Picture & Steam Input)**, **Wine/Proton**, **Lutris**, **Heroic**, **Emulators (PCSX2, RPCS3, Dolphin)**, and **Web Gamepad API**.

---

## Quick Installation

Clone this repository and run the automated installer:

```bash
git clone https://github.com/SawanTeja/Third-Party-Controller-Fix-For-Linux.git ControllerDriver
cd ControllerDriver
sudo ./install.sh
```

The installer will:
1. Compile the driver binary (`cosmic-xbox-driver`).
2. Install it to `/usr/local/bin/cosmic-xbox-driver`.
3. Set up udev rules for controller access (`99-cosmic-xbox.rules`).
4. Install and enable the background systemd service (`cosmic-xbox-driver.service`).

---

## Verifying It Works

### 1. Check Service Status
```bash
systemctl status cosmic-xbox-driver.service
```

### 2. Test Analog Trigger Sensitivity
Run the included trigger monitor:
```bash
python3 monitor_triggers.py
```
Gently squeeze L2 and R2—you will see smooth, continuous analog values from `0` to `255`!

### 3. Test Vibration
Run the rumble test on the virtual Xbox controller:
```bash
python3 test_rumble.py
```
The controller will vibrate strong and weak motors for 1 second.

### 4. Test in Browser
Open [gamepad-tester.com](https://gamepad-tester.com/) in Chrome or Firefox. It will detect:
```
Xbox 360 Controller (XInput STANDARD GAMEPAD)
Vendor: 045e Product: 028e
```
Both triggers and vibration tests will work out of the box!

---

## Uninstallation

To cleanly remove the driver and restore your system:

```bash
sudo ./uninstall.sh
```

---

## Supported Controllers

- **Cosmic Byte Blitz** (Wireless Dongle & Wired)
- **ShenZhen ShanWan Technology Gamepads** (`20bc:5001`)
- **ShanWan USB Wireless Gamepad** (`2563:0575`, `2563:0523`)
- Other third-party PC/Android controllers using ShanWan chipsets

---

## Architecture Details

```
 [ Physical Controller: Cosmic Byte Blitz ]
                   │
           (USB: 20bc:5001)
                   ▼
       [ Linux Kernel /dev/input/eventX ]
                   │ (EVIOCGRAB exclusive lock)
                   ▼
     [ cosmic-xbox-driver (Daemon) ]
          │                    │
 (Inputs translated)    (Rumble forwarded)
          │                    │
          ▼                    ▼
   [ /dev/uinput ]      [ /dev/hidrawY ]
          │                    │
 (Virtual 045e:028e)           ▼
          │           [ Motor Vibration ]
          ▼
 [ Steam / Wine / Proton / Games / Browser ]
```

- **CPU Overhead**: 0% idle, <0.1ms input latency (driven by Linux `epoll`).
- **Memory Footprint**: ~1.7 MB RSS.
- **Kernel Compatibility**: Tested on Linux 6.x and 7.x kernels (Ubuntu 24.04, 26.04, Arch, Fedora).
