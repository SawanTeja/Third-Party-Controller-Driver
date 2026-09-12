/*
 * cosmic-xbox-driver.c - True analog triggers support
 * Maps ABS_BRAKE -> ABS_Z (LT) and ABS_GAS -> ABS_RZ (RT)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <linux/input.h>

// Full 8-bit analog resolution 0..255 preserved
