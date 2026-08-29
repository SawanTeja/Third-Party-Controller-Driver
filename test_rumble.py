#!/usr/bin/env python3
import sys, os, struct, time, fcntl

EVENT_PATH = sys.argv[1] if len(sys.argv) > 1 else "/dev/input/event18"
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
finally:
    os.close(fd)
