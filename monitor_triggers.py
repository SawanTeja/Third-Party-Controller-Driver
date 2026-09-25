#!/usr/bin/env python3
import sys, os, struct, time

def find_gamepad_device():
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # 1. Prefer virtual Xbox 360 controller
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
        
        # 2. Fallback to raw gamepad
        for ev in sorted(os.listdir("/sys/class/input")):
            if ev.startswith("event"):
                name_file = f"/sys/class/input/{ev}/device/name"
                if os.path.exists(name_file):
                    try:
                        with open(name_file, "r") as f:
                            name = f.read().strip()
                            if any(k in name.lower() for k in ["gamepad", "joystick", "shanwan", "blitz"]):
                                return f"/dev/input/{ev}"
                    except Exception:
                        pass

    # 3. Proc scan
    if os.path.exists("/proc/bus/input/devices"):
        try:
            with open("/proc/bus/input/devices", "r") as f:
                content = f.read()
                devices = content.split("\n\n")
                for dev in devices:
                    if 'Name="Microsoft X-Box 360 pad"' in dev:
                        for line in dev.splitlines():
                            if line.startswith("H: Handlers="):
                                for part in line.split():
                                    if part.startswith("event"):
                                        return f"/dev/input/{part}"
        except Exception:
            pass

    return None

EVENT_PATH = find_gamepad_device()
if not EVENT_PATH:
    print("[-] Error: No gamepad or virtual Xbox 360 controller found.")
    print("    Please ensure cosmic-xbox-driver is running or controller is connected.")
    sys.exit(1)

# struct input_event
EVENT_FORMAT = "qqHHi"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

EV_KEY = 0x01
EV_ABS = 0x03

ABS_BRAKE = 0x0a # LT
ABS_GAS   = 0x09 # RT
ABS_Z     = 0x02
ABS_RZ    = 0x05

print(f"Monitoring trigger sensitivity on {EVENT_PATH} for 10 seconds...")
print("Gently squeeze and release L2 and R2 triggers now to observe analog sensitivity!")

try:
    fd = os.open(EVENT_PATH, os.O_RDONLY | os.O_NONBLOCK)
except Exception as e:
    print(f"Error opening {EVENT_PATH}: {e}")
    sys.exit(1)

start_time = time.time()
lt_val, rt_val = 0, 0

while time.time() - start_time < 10:
    try:
        data = os.read(fd, EVENT_SIZE * 16)
        if not data:
            time.sleep(0.01)
            continue
        for i in range(0, len(data), EVENT_SIZE):
            sec, usec, ev_type, ev_code, ev_val = struct.unpack(EVENT_FORMAT, data[i:i+EVENT_SIZE])
            if ev_type == EV_ABS:
                if ev_code in (ABS_BRAKE, ABS_Z):
                    lt_val = ev_val
                    print(f"\r[TRIGGERS] L2 (LT): {lt_val:3d} / 255  |  R2 (RT): {rt_val:3d} / 255", end="", flush=True)
                elif ev_code in (ABS_GAS, ABS_RZ):
                    rt_val = ev_val
                    print(f"\r[TRIGGERS] L2 (LT): {lt_val:3d} / 255  |  R2 (RT): {rt_val:3d} / 255", end="", flush=True)
            elif ev_type == EV_KEY:
                if ev_code in (0x138, 0x139, 0x136, 0x137):
                    btn = "L2" if ev_code in (0x138, 0x136) else "R2"
                    state = "PRESSED" if ev_val else "RELEASED"
                    print(f"\n[BUTTON] {btn} click: {state}")
    except BlockingIOError:
        time.sleep(0.01)
    except Exception as e:
        print("Read error:", e)
        break

os.close(fd)
print("\nDone monitoring.")
