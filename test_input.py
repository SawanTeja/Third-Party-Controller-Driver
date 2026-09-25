#!/usr/bin/env python3
import sys, os, struct, time

def find_input_device():
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

    return None

EVENT_PATH = find_input_device()
if not EVENT_PATH:
    print("[-] Error: Controller input device not found.")
    sys.exit(1)

# struct input_event:
# timeval: 16 bytes (tv_sec: 8 bytes, tv_usec: 8 bytes)
# type: 2 bytes (__u16)
# code: 2 bytes (__u16)
# value: 4 bytes (__s32)
EVENT_FORMAT = "qqHHi"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_FF  = 0x15

KEY_NAMES = {
    0x130: "BTN_SOUTH / BTN_A",
    0x131: "BTN_EAST / BTN_B",
    0x132: "BTN_C",
    0x133: "BTN_NORTH / BTN_X",
    0x134: "BTN_WEST / BTN_Y",
    0x135: "BTN_Z",
    0x136: "BTN_TL / LB",
    0x137: "BTN_TR / RB",
    0x138: "BTN_TL2 / LT",
    0x139: "BTN_TR2 / RT",
    0x13a: "BTN_SELECT / BACK",
    0x13b: "BTN_START / START",
    0x13c: "BTN_MODE / HOME",
    0x13d: "BTN_THUMBL / L3",
    0x13e: "BTN_THUMBR / R3",
}

ABS_NAMES = {
    0x00: "ABS_X (Left Stick X)",
    0x01: "ABS_Y (Left Stick Y)",
    0x02: "ABS_Z (Left Trigger LT)",
    0x03: "ABS_RX (Right Stick X)",
    0x04: "ABS_RY (Right Stick Y)",
    0x05: "ABS_RZ (Right Trigger RT)",
    0x10: "ABS_HAT0X (D-Pad X)",
    0x11: "ABS_HAT0Y (D-Pad Y)",
}

print(f"Opening {EVENT_PATH}...")
try:
    fd = os.open(EVENT_PATH, os.O_RDONLY | os.O_NONBLOCK)
except Exception as e:
    print(f"Error opening {EVENT_PATH}: {e}")
    sys.exit(1)

print("Listening for input events for 10 seconds. Press buttons or move sticks now...")
start_time = time.time()
while time.time() - start_time < 10:
    try:
        data = os.read(fd, EVENT_SIZE * 10)
        if not data:
            time.sleep(0.01)
            continue
        for i in range(0, len(data), EVENT_SIZE):
            chunk = data[i:i+EVENT_SIZE]
            if len(chunk) < EVENT_SIZE:
                continue
            sec, usec, ev_type, ev_code, ev_val = struct.unpack(EVENT_FORMAT, chunk)
            if ev_type == EV_KEY:
                name = KEY_NAMES.get(ev_code, f"KEY_0x{ev_code:03x}")
                action = "PRESSED" if ev_val == 1 else ("RELEASED" if ev_val == 0 else "REPEAT")
                print(f"[BUTTON] code=0x{ev_code:03x} ({name}): {action}")
            elif ev_type == EV_ABS:
                name = ABS_NAMES.get(ev_code, f"ABS_0x{ev_code:02x}")
                # print significant changes or hat
                if ev_code in (0x02, 0x05, 0x10, 0x11) or abs(ev_val) > 4000:
                    print(f"[AXIS] code=0x{ev_code:02x} ({name}): value={ev_val}")
    except BlockingIOError:
        time.sleep(0.01)
    except Exception as e:
        print("Read error:", e)
        break

os.close(fd)
print("Done listening.")
