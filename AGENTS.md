# AGENTS.md

## Project Overview

ZMK firmware configuration for **KimiBoard** — a custom 4-key keyboard with a PMW3610 trackball, running on a Seeed XIAO BLE (nRF52840). Uses `zmk-rgbled-widget` for status indication. Build and flash instructions are in the README. Upstream dependencies are pinned to fixed SHAs; see "Updating pinned versions" in the README to bump them.

## Caveats

- **Keymap position order is reversed from physical order**: the matrix transform maps SW4=0 (reset), SW3=1, SW2=2, SW1=3. Combo `key-positions` use this order.
- **Keys 2 & 3 are hold-taps** (`mo_mkp`, tap-preferred, 200 ms): tap = mouse click (middle / right), hold = momentary gesture layer. Key 3 hold defaults to `DESKTOP`; the Key 2 + Key 3 combo toggles `RECTANGLE_OVERRIDE`, which changes Key 3 hold to `RECTANGLE`.
- **Three independent gesture nodes**, all locally defined: `zip_scroll_gesture` (Scroll & Navigate, active on the SCROLL layer), `zip_desktop_gesture` (macOS Spaces & Mission Control, active on the DESKTOP layer), and `zip_rectangle_gesture` (Rectangle.app window management, active on the RECTANGLE layer).
- **Trackball**: 600 CPI, smart-mode. Axes are intentionally swapped — sensor X → cursor Y, sensor Y → cursor X (due to physical mounting orientation), and only sensor X is inverted. The SCROLL layer inverts scroll direction to match macOS natural (two-finger trackpad) scrolling (`&zip_scroll_scaler (-1) 32`).
- **ZMK Studio physical layout**: defined in `.overlay` only. Studio uses this to render the keyboard visually.
