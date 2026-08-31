#!/usr/bin/env python3
import sys, os, time

HIDRAW_PATH = "/dev/hidraw3"
print(f"Testing Left (Heavy) and Right (Light) motors on {HIDRAW_PATH}...")

fd = os.open(HIDRAW_PATH, os.O_RDWR)

try:
    print("Testing ShanWan 8-byte rumble format...")
    # Strong motor only: 0x02, 0x08, weak=0, strong=0xff, duration=0xff, 0, 0, 0
    print(">> Pulses STRONG MOTOR (Left) for 1 second <<")
    os.write(fd, bytes([0x02, 0x08, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00]))
    time.sleep(1.0)
    os.write(fd, bytes([0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    time.sleep(0.5)

    # Weak motor only: 0x02, 0x08, weak=0xff, strong=0, duration=0xff, 0, 0, 0
    print(">> Pulses WEAK MOTOR (Right) for 1 second <<")
    os.write(fd, bytes([0x02, 0x08, 0xff, 0x00, 0xff, 0x00, 0x00, 0x00]))
    time.sleep(1.0)
    os.write(fd, bytes([0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    time.sleep(0.5)

    print(">> Pulses BOTH MOTORS for 1 second <<")
    os.write(fd, bytes([0x02, 0x08, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00]))
    time.sleep(1.0)
    os.write(fd, bytes([0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
except Exception as e:
    print("Error:", e)
finally:
    os.close(fd)
print("Motor test finished!")
