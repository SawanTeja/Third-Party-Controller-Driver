#!/usr/bin/env python3
import sys, os, time

def find_hidraw_device():
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    if os.path.exists("/sys/class/hidraw"):
        for h in sorted(os.listdir("/sys/class/hidraw")):
            uevent_file = f"/sys/class/hidraw/{h}/device/uevent"
            if os.path.exists(uevent_file):
                try:
                    with open(uevent_file, "r") as f:
                        content = f.read().lower()
                        # Check for ShanWan / Cosmic Byte / Gamepad IDs
                        targets = ["05ac:033e", "20bc:5001", "2563:0575", "2563:0523", "2563:0526", "2563:0599", "gamepad", "shanwan"]
                        if any(t in content for t in targets):
                            return f"/dev/{h}"
                except Exception:
                    pass

    return "/dev/hidraw3" if os.path.exists("/dev/hidraw3") else None

HIDRAW_PATH = find_hidraw_device()
if not HIDRAW_PATH or not os.path.exists(HIDRAW_PATH):
    print("[-] Error: Controller hidraw device not found.")
    print("    Please check if controller is connected with 'ls -l /dev/hidraw*'.")
    sys.exit(1)

print(f"Testing Left (Heavy) and Right (Light) motors on {HIDRAW_PATH}...")

try:
    fd = os.open(HIDRAW_PATH, os.O_RDWR)
except PermissionError:
    print(f"[-] Permission denied opening {HIDRAW_PATH}.")
    print("    Please reload udev rules or run with sudo:")
    print("    sudo udevadm control --reload-rules && sudo udevadm trigger")
    sys.exit(1)
except Exception as e:
    print(f"[-] Error opening {HIDRAW_PATH}: {e}")
    sys.exit(1)

def send_rumble(strong, weak, duration=0xff):
    # Try standard ShanWan 8-byte packet
    pkt8 = bytes([0x02, 0x08, weak, strong, duration, 0x00, 0x00, 0x00])
    try:
        os.write(fd, pkt8)
    except Exception:
        pass
    # Also try 5-byte report ID 2 packet
    pkt5 = bytes([0x02, strong, weak, duration, 0x00])
    try:
        os.write(fd, pkt5)
    except Exception:
        pass

def stop_rumble():
    stop8 = bytes([0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    stop5 = bytes([0x02, 0x00, 0x00, 0x00, 0x00])
    try:
        os.write(fd, stop8)
    except Exception:
        pass
    try:
        os.write(fd, stop5)
    except Exception:
        pass

try:
    print(">> Pulses STRONG MOTOR (Left) for 1 second <<")
    send_rumble(strong=0xff, weak=0x00)
    time.sleep(1.0)
    stop_rumble()
    time.sleep(0.5)

    print(">> Pulses WEAK MOTOR (Right) for 1 second <<")
    send_rumble(strong=0x00, weak=0xff)
    time.sleep(1.0)
    stop_rumble()
    time.sleep(0.5)

    print(">> Pulses BOTH MOTORS for 1 second <<")
    send_rumble(strong=0xff, weak=0xff)
    time.sleep(1.0)
    stop_rumble()
finally:
    stop_rumble()
    os.close(fd)

print("Motor test finished!")
