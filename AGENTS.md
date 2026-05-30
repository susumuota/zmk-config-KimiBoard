# AGENTS.md

## Project Overview

ZMK firmware configuration for **KimiBoard** — a custom 4-key keyboard with a PMW3610 trackball, running on a Seeed XIAO BLE (nRF52840). Uses `zmk-rgbled-widget` for status indication. Build and flash instructions are in the README. Upstream dependencies are pinned to fixed SHAs; see "Updating pinned versions" in the README to bump them.

## Caveats

- **Keymap position order is reversed from physical order**: the matrix transform maps SW4=0, SW3=1, SW2=2, SW1=3. Combo `key-positions` use this order.
- **Trackball axes are intentionally swapped**: sensor X → cursor Y, sensor Y → cursor X (due to physical mounting orientation). Only sensor X is inverted.
- **ZMK Studio physical layout**: defined in `.overlay` only. Studio uses this to render the keyboard visually.
