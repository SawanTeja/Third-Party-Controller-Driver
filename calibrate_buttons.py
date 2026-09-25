#!/usr/bin/env python3
import sys, os, struct, time

# Search for the raw hardware controller (05ac:033e, 20bc:5001, etc.)
def find_raw_device():
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    if os.path.exists("/sys/class/input"):
        for ev in sorted(os.listdir("/sys/class/input")):
            if ev.startswith("event"):
                name_file = f"/sys/class/input/{ev}/device/name"
                if os.path.exists(name_file):
                    try:
                        with open(name_file, "r") as f:
                            name = f.read().strip()
                            if "Microsoft" not in name and any(k in name.lower() for k in ["gamepad", "joystick", "shanwan", "blitz"]):
                                return f"/dev/input/{ev}"
                    except Exception:
                        pass
    return "/dev/input/event18"

DEV = find_raw_device()
print(f"Opening raw controller device: {DEV}")
try:
    fd = os.open(DEV, os.O_RDONLY | os.O_NONBLOCK)
except Exception as e:
    print(f"Error opening {DEV}: {e}")
    sys.exit(1)

EVENT_FORMAT = "qqHHi"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

BUTTONS_TO_TEST = [
    ("A", "Bottom button (A / Cross)"),
    ("B", "Right button (B / Circle)"),
    ("X", "Left button (X / Square)"),
    ("Y", "Top button (Y / Triangle)"),
    ("LB", "Left Bumper / Shoulder (LB / L1)"),
    ("RB", "Right Bumper / Shoulder (RB / R1)"),
    ("LT", "Left Trigger (LT / L2 click or pull)"),
    ("RT", "Right Trigger (RT / R2 click or pull)"),
    ("SELECT", "Back / Select button"),
    ("START", "Start button"),
    ("L3", "Left Stick Click (Press down left stick)"),
    ("R3", "Right Stick Click (Press down right stick)"),
    ("HOME", "Home / Guide / Mode button"),
]

recorded_map = {}

print("=" * 60)
print("  Controller Hardware Button Calibrator")
print("  Press each requested button when prompted.")
print("=" * 60)

# Flush any existing pending events
try:
    while True:
        d = os.read(fd, 1024)
        if not d: break
except BlockingIOError:
    pass

for btn_name, desc in BUTTONS_TO_TEST:
    print(f"\n--> Please press: [{btn_name}] ({desc}) ...", flush=True)
    detected = False
    start_t = time.time()
    while time.time() - start_t < 15:
        try:
            data = os.read(fd, EVENT_SIZE * 8)
            if not data:
                time.sleep(0.01)
                continue
            for i in range(0, len(data), EVENT_SIZE):
                chunk = data[i:i+EVENT_SIZE]
                if len(chunk) < EVENT_SIZE: continue
                sec, usec, ev_type, ev_code, ev_val = struct.unpack(EVENT_FORMAT, chunk)
                if ev_type == 1 and ev_val == 1: # EV_KEY PRESSED
                    print(f"    [DETECTED KEY] code=0x{ev_code:03x} ({ev_code}) for {btn_name}")
                    recorded_map[btn_name] = ("KEY", hex(ev_code))
                    detected = True
                    break
                elif ev_type == 3 and ev_val > 200 and ev_code in (0x02, 0x05, 0x09, 0x0a): # EV_ABS Trigger
                    print(f"    [DETECTED AXIS TRIGGER] axis=0x{ev_code:02x} val={ev_val} for {btn_name}")
                    recorded_map[btn_name] = ("ABS", hex(ev_code))
                    detected = True
                    break
            if detected:
                # Wait for release
                time.sleep(0.3)
                # Flush
                try:
                    while True:
                        if not os.read(fd, 1024): break
                except BlockingIOError:
                    pass
                break
        except BlockingIOError:
            time.sleep(0.01)
    if not detected:
        print(f"    [SKIPPED] No press detected for {btn_name}")

os.close(fd)

print("\n" + "=" * 60)
print("CALIBRATION RESULTS:")
for k, v in recorded_map.items():
    print(f"  {k:8s} -> {v[0]} {v[1]}")
print("=" * 60)

import json
with open("button_map.json", "w") as f:
    json.dump(recorded_map, f, indent=2)
print("Saved mapping to button_map.json successfully!")
