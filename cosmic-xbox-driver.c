/*
 * cosmic-xbox-driver.c - Stick scaling
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static inline int32_t scale_axis_255(int32_t val) {
    if (val >= 124 && val <= 132) return 0;
    int32_t centered = val - 128;
    int32_t scaled = (centered * 65535) / 255;
    if (scaled < -32768) scaled = -32768;
    if (scaled > 32767) scaled = 32767;
    return scaled;
}
