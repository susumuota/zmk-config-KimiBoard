# ZMK Config for KimiBoard

<img width="1920" height="1080" alt="KimiBoard switches" src="https://github.com/user-attachments/assets/21cd87cc-cafe-45ed-b6bb-a46061c3a2e3" />

A 4-key Bluetooth/USB keyboard with a PMW3610 trackball, built on the Seeed XIAO BLE (nRF52840). Supports up to 3 Bluetooth pairings and includes an RGB LED status widget.

[ZMK Studio](https://zmk.studio/) is enabled, allowing keymap customization without reflashing.

## Default Keymap

| Key | Assignment |
|:-|:-|
| Key 0 | Switch Bluetooth connection (cycle through 1 → 2 → 3) |
| Key 1 | Left click |
| Key 2 | Middle click |
| Key 3 | Right click |
| Key 0 + Key 3 | Clear current Bluetooth pairing |

The trackball provides pointer movement (400 CPI, smart-mode enabled).

## Building

Firmware is built automatically via GitHub Actions on push or pull request. Download the `.uf2` artifacts from the Actions run page.

Two firmware images are produced:
- **kimiboard** — main firmware with ZMK Studio support
- **settings_reset** — utility firmware to reset stored settings
