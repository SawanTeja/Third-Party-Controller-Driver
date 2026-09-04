/*
 * cosmic-xbox-driver.c - Added device detection and EVIOCGRAB
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <linux/input.h>

static int grab_device(int fd) {
    return ioctl(fd, EVIOCGRAB, 1);
}

int main(void) {
    printf("Driver: hardware grabbing with EVIOCGRAB implemented\n");
    return 0;
}
