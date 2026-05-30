# AGENTS.md

## Project Overview

ZMK firmware configuration for **KimiBoard** — a custom 4-key keyboard with a PMW3610 trackball, running on a Seeed XIAO BLE (nRF52840). The board communicates via Bluetooth (up to 3 paired devices) or USB, and uses the `zmk-rgbled-widget` for status indication.

## Build

Firmware is built exclusively via **GitHub Actions**. Push to `main` (or open a PR) to trigger the workflow, which calls `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3`. There is no local build — no `west build` or toolchain setup is expected in this repo.

The `build.yaml` defines two build targets:
- `xiao_ble//zmk` + shield `kimiboard rgbled_adapter` (with ZMK Studio enabled)
- `xiao_ble//zmk` + shield `settings_reset`

Download the built `.uf2` artifacts from the Actions run.

## Architecture

### Shield definition (`config/boards/shields/kimi/`)

| File | Purpose |
|---|---|
| `kimiboard.overlay` | Hardware definition: GPIO matrix (4 rows x 5 cols), SPI trackball (PMW3610), pin mappings, physical key layout |
| `kimiboard.dtsi` | Physical layout metadata for ZMK Studio |
| `kimiboard.keymap` | Keymap and combos (default layer + combo definitions) |
| `kimiboard.conf` | Kconfig: BT/USB device names, trackball driver, mouse support, RGB LED widget |
| `kimiboard.defconfig` | Sets default keyboard name |
| `Kconfig.shield` | Shield detection macro |
| `kimiboard.zmk.yml` | ZMK metadata (shield type, required board) |

### West manifest (`config/west.yml`)

Pulls in two upstream projects:
- `zmkfirmware/zmk` (main) — core firmware
- `caksoylar/zmk-rgbled-widget` (main) — RGB LED status widget

### Key hardware details

- **MCU**: nRF52840 (Seeed XIAO BLE)
- **Trackball**: PMW3610 on SPI0 (CS: gpio0 pin 9, motion: gpio0 pin 2), 400 CPI, both axes inverted, smart-mode enabled
- **Matrix**: col2row, 4 switches mapped via `zmk,matrix-transform`
- **Key 0 (SW1)**: small utility key (50u wide); Keys 1-3 (SW2-SW4): full-size (100u)

## Keymap conventions

The keymap uses ZMK combos for multi-key actions (e.g., `key-positions <0 3>` for BT_CLR). When modifying the keymap, preserve combo timeout values and key-position indices, which correspond to the matrix transform order (SW4=0, SW3=1, SW2=2, SW1=3, reversed from physical order).

## ZMK Studio

ZMK Studio is enabled (`CONFIG_ZMK_STUDIO=y`, locking disabled). The physical layout in both `.dtsi` and `.overlay` must stay in sync — Studio uses these to render the keyboard visually.
