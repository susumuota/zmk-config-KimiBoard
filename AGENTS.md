# AGENTS.md

## Project Overview

ZMK firmware config for **KimiBoard**, a 4-key keyboard with a PMW3610 trackball on a Seeed XIAO BLE (nRF52840). See the README for build/flash and dependency details.

## Caveats

- **Keymap position order is reversed from physical order**: the matrix transform maps SW4=0 (reset), SW3=1, SW2=2, SW1=3. Combo `key-positions` use this order.
- **Key 2 is a plain momentary layer** (`&mo SCROLL`): no tap, pressing it enters the SCROLL layer instantly (no hold-tap delay), releasing exits. **Key 3 is a hold-tap** (`mo_mkp`, tap-preferred, 200 ms): tap = right click, hold = momentary gesture layer. Key 3 hold defaults to `DESKTOP`; the Key 2 + Key 3 combo toggles `RECTANGLE_OVERRIDE`, which changes Key 3 hold to `RECTANGLE`.
- **Three independent gesture nodes**, all locally defined: `zip_scroll_gesture` (Scroll & Navigate, active on the SCROLL layer), `zip_desktop_gesture` (macOS Spaces & Mission Control, active on the DESKTOP layer), and `zip_rectangle_gesture` (Rectangle.app window management, active on the RECTANGLE layer).
- **Trackball**: 400 CPI, smart-mode. Axes are intentionally swapped (sensor X → cursor Y, sensor Y → cursor X, due to physical mounting orientation), and only sensor X is inverted. The SCROLL layer inverts scroll direction to match macOS natural (two-finger trackpad) scrolling (`&zip_scroll_scaler (-1) 48`).
