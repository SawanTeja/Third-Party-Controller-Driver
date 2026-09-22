CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra
TARGET = cosmic-xbox-driver
SRC = cosmic-xbox-driver.c

PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
SYSTEMDDIR ?= /etc/systemd/system
UDEVDIR ?= /etc/udev/rules.d

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 $(TARGET) $(DESTDIR)$(BINDIR)/$(TARGET)
	install -d $(DESTDIR)$(UDEVDIR)
	install -m 644 99-cosmic-xbox.rules $(DESTDIR)$(UDEVDIR)/99-cosmic-xbox.rules
	install -d $(DESTDIR)$(SYSTEMDDIR)
	install -m 644 cosmic-xbox-driver.service $(DESTDIR)$(SYSTEMDDIR)/cosmic-xbox-driver.service
	udevadm control --reload-rules && udevadm trigger
	systemctl daemon-reload
	systemctl enable --now cosmic-xbox-driver.service

uninstall:
	systemctl stop cosmic-xbox-driver.service || true
	systemctl disable cosmic-xbox-driver.service || true
	rm -f $(DESTDIR)$(SYSTEMDDIR)/cosmic-xbox-driver.service
	rm -f $(DESTDIR)$(UDEVDIR)/99-cosmic-xbox.rules
	rm -f $(DESTDIR)$(BINDIR)/$(TARGET)
	udevadm control --reload-rules
	systemctl daemon-reload

.PHONY: all clean install uninstall
