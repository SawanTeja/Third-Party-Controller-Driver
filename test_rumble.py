#!/usr/bin/env python3
import sys, os, struct, time, fcntl

def find_xbox_device():
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # 1. Search for virtual Xbox 360 controller created by the driver
    if os.path.exists("/sys/class/input"):
        for ev in sorted(os.listdir("/sys/class/input")):
            if ev.startswith("event"):
                name_file = f"/sys/class/input/{ev}/device/name"
                if os.path.exists(name_file):
                    try:
                        with open(name_file, "r") as f:
                            name = f.read().strip()
                            if "Microsoft X-Box 360 pad" in name or "Xbox 360" in name:
                                return f"/dev/input/{ev}"
                    except Exception:
                        pass

    # 2. Check /proc/bus/input/devices for Handlers
    if os.path.exists("/proc/bus/input/devices"):
        try:
            with open("/proc/bus/input/devices", "r") as f:
                content = f.read()
                devices = content.split("\n\n")
                for dev in devices:
                    if 'Name="Microsoft X-Box 360 pad"' in dev or 'Name="Microsoft Xbox 360' in dev:
                        for line in dev.splitlines():
                            if line.startswith("H: Handlers="):
                                for part in line.split():
                                    if part.startswith("event"):
                                        return f"/dev/input/{part}"
        except Exception:
            pass

    return None

EVENT_PATH = find_xbox_device()
if not EVENT_PATH:
    print("[-] Error: Virtual 'Microsoft X-Box 360 pad' not found.")
    print("    Please ensure cosmic-xbox-driver is running:")
    print("    systemctl status cosmic-xbox-driver.service")
    sys.exit(1)

EVIOCSFF = 0x40304580 # _IOW("E", 0x80, struct ff_effect)

print(f"Opening {EVENT_PATH} for Force Feedback test...")
try:
    fd = os.open(EVENT_PATH, os.O_RDWR)
except Exception as e:
    print(f"Error opening {EVENT_PATH}: {e}")
    sys.exit(1)

# Upload rumble effect (length: 1000ms, strong: 0xffff, weak: 0xffff)
effect_data = struct.pack("HhHHHHHHH30s", 0x50, -1, 0, 0, 0, 1000, 0, 0xffff, 0xffff, b"\x00"*30)
buf = bytearray(effect_data)

try:
    fcntl.ioctl(fd, EVIOCSFF, buf)
    effect_id = struct.unpack("h", buf[2:4])[0]
    print(f"Uploaded rumble effect ID: {effect_id}")
    
    # Play
    print(">>> VIBRATING NOW (1 second) <<<")
    play_event = struct.pack("qqHHi", 0, 0, 0x15, effect_id, 1)
    os.write(fd, play_event)
    time.sleep(1.2)
    
    # Stop
    stop_event = struct.pack("qqHHi", 0, 0, 0x15, effect_id, 0)
    os.write(fd, stop_event)
    print("Vibration test complete.")
except Exception as e:
    print(f"Rumble error: {e}")
    if "Function not implemented" in str(e):
        print("Note: The device node you opened does not support Force Feedback (EV_FF).")
        print("Make sure you are testing the virtual Xbox 360 controller created by cosmic-xbox-driver.")
finally:
    os.close(fd)
