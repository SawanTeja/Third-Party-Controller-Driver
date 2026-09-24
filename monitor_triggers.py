#!/usr/bin/env python3
import sys, os, struct, time

EVENT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/dev/input/event18"

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

fd = os.open(EVENT_PATH, os.O_RDONLY | os.O_NONBLOCK)
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
                if ev_code in (0x138, 0x139):
                    btn = "L2" if ev_code == 0x138 else "R2"
                    state = "PRESSED" if ev_val else "RELEASED"
                    print(f"\n[BUTTON] {btn} click: {state}")
    except BlockingIOError:
        time.sleep(0.01)

os.close(fd)
print("\nDone monitoring.")
