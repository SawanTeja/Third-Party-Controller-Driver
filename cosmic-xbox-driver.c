/*
 * cosmic-xbox-driver.c - Dual rumble engine
 */
#define _GNU_SOURCE
#include <stdint.h>
// Writes ShanWan rumble packet: 0x02, 0x08, weak, strong, 0xff, 0, 0, 0
