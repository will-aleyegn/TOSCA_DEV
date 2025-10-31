# GPIO Safety Interlocks - DEPRECATED

**WARNING: This folder contains deprecated FT232H-based documentation.**

**Current GPIO implementation uses Arduino Nano with PyFirmata.**

---

## Current Documentation

**See:** [../gpio_arduino/ARDUINO_SETUP.md](../gpio_arduino/ARDUINO_SETUP.md)

The TOSCA GPIO controller now uses:
- **Hardware:** Arduino Nano (ATmega328P)
- **Protocol:** Firmata (StandardFirmata)
- **Library:** pyfirmata (Python)
- **Advantages:** Cross-platform, built-in ADC, simpler wiring, USB power+data

---

## Legacy Documentation

If you need the old FT232H documentation, see:
- [README_FT232H_DEPRECATED.md](README_FT232H_DEPRECATED.md)

**Note:** FT232H support has been removed from the codebase as of 2025-10-24.

---

**Last Updated:** 2025-10-24
