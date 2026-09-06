/*
 * cosmic-xbox-driver.c - uinput virtual Xbox 360 pad setup
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/input.h>
#include <linux/uinput.h>

static int create_uinput_xbox360(void) {
    int fd = open("/dev/uinput", O_RDWR | O_NONBLOCK);
    if (fd < 0) return -1;
    ioctl(fd, UI_SET_EVBIT, EV_KEY);
    ioctl(fd, UI_SET_KEYBIT, BTN_A);
    ioctl(fd, UI_SET_KEYBIT, BTN_B);
    ioctl(fd, UI_SET_KEYBIT, BTN_X);
    ioctl(fd, UI_SET_KEYBIT, BTN_Y);
    struct uinput_setup usetup;
    memset(&usetup, 0, sizeof(usetup));
    snprintf(usetup.name, UINPUT_MAX_NAME_SIZE, "Microsoft X-Box 360 pad");
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x045e;
    usetup.id.product = 0x028e;
    ioctl(fd, UI_DEV_SETUP, &usetup);
    ioctl(fd, UI_DEV_CREATE);
    return fd;
}

int main(void) {
    int ufd = create_uinput_xbox360();
    if (ufd >= 0) close(ufd);
    return 0;
}
