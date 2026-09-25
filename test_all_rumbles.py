#!/usr/bin/env python3
import sys, os, time, fcntl

def find_hidraw():
    if len(sys.argv) > 1: return sys.argv[1]
    if os.path.exists("/sys/class/hidraw"):
        for h in sorted(os.listdir("/sys/class/hidraw")):
            uevent = f"/sys/class/hidraw/{h}/device/uevent"
            if os.path.exists(uevent):
                with open(uevent) as f:
                    c = f.read().lower()
                    if any(x in c for x in ["05ac:033e", "20bc:5001", "2563:", "gamepad"]):
                        return f"/dev/{h}"
    return "/dev/hidraw3"

dev_path = find_hidraw()
print(f"Opening {dev_path} for Rumble Diagnostic Test...")
fd = os.open(dev_path, os.O_RDWR)

def stop_all():
    # Stop packets for all known formats
    stops = [
        bytes([0x02, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
        bytes([0x00, 0x00, 0x00, 0x00, 0x00]),
    ]
    for s in stops:
        try: os.write(fd, s)
        except: pass
        try: fcntl.ioctl(fd, (3 << 30) | (len(s) << 16) | (ord('H') << 8) | 0x0b, bytearray(s))
        except: pass

PATTERNS = [
    ("Pattern 1 (Betop 5-byte: 02 00 00 FF FF)", bytes([0x02, 0x00, 0x00, 0xff, 0xff])),
    ("Pattern 2 (ShanWan 8-byte: 02 08 FF FF FF 00 00 00)", bytes([0x02, 0x08, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00])),
    ("Pattern 3 (Direct 5-byte: 02 FF FF FF 00)", bytes([0x02, 0xff, 0xff, 0xff, 0x00])),
    ("Pattern 4 (DragonRise 8-byte: 01 00 00 FF FF 00 00 00)", bytes([0x01, 0x00, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00])),
    ("Pattern 5 (DragonRise 0x51: 00 51 00 FF 00 FF)", bytes([0x00, 0x51, 0x00, 0xff, 0x00, 0xff])),
    ("Pattern 6 (ShanWan 9-byte [Report 0]: 00 02 08 FF FF FF 00 00 00)", bytes([0x00, 0x02, 0x08, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00])),
    ("Pattern 7 (4-byte: 02 03 FF FF)", bytes([0x02, 0x03, 0xff, 0xff])),
    ("Pattern 8 (LED Output: 02 FF 00 FF 00)", bytes([0x02, 0xff, 0x00, 0xff, 0x00])),
]

print("\nStarting test! Pay attention to whether the controller vibrates on any pattern.\n")

for name, pkt in PATTERNS:
    print(f"---> Testing {name} ...", flush=True)
    # Test via write()
    try:
        os.write(fd, pkt)
    except Exception as e:
        print(f"     write error: {e}")
    # Also test via HIDIOCSOUTPUT ioctl
    try:
        buf = bytearray(pkt)
        ioctl_num = (3 << 30) | (len(pkt) << 16) | (ord('H') << 8) | 0x0b
        fcntl.ioctl(fd, ioctl_num, buf)
    except Exception as e:
        pass
    
    time.sleep(1.8)
    stop_all()
    time.sleep(0.5)

os.close(fd)
print("\nTest completed!")
