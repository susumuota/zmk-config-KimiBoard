# ZMK Config for KimiBoard

<img width="1920" height="1080" alt="KimiBoard switches" src="https://github.com/user-attachments/assets/0d2e7812-2c09-40fd-a618-07bce5b48ad3" />

This repository is a [ZMK](https://zmk.dev/) firmware configuration for sirocom's [KimiBoard](https://github.com/sirocominfo/zmk-config-KimiBoard), a 4-key Bluetooth/USB keyboard with a [PMW3610](https://www.pixart.com/products-detail/21/PMW3610DM-SUDU) trackball built on the [Seeed XIAO BLE](https://wiki.seeedstudio.com/XIAO_BLE/) (nRF52840). It supports up to 3 Bluetooth pairings, [mouse gestures](https://github.com/kot149/zmk-mouse-gesture) (scrolling, forward/back, and window management) via the trackball, and includes an [RGB LED status widget](https://github.com/caksoylar/zmk-rgbled-widget).

The KimiBoard is available for purchase at [sirocom's BOOTH shop](https://sirocom.booth.pm/items/8301933).

## Credits

This repository is a fork of [sirocominfo/zmk-config-KimiBoard](https://github.com/sirocominfo/zmk-config-KimiBoard) by sirocominfo. Many thanks to the original author for the hardware design, base configuration, and the header photo.

## Default Keymap

Keys 2 and 3 are hold-taps (`mo_mkp`, tap-preferred, 200 ms): a quick tap sends a mouse
click, while holding activates a momentary gesture layer.

| Key | Tap | Hold (≥200 ms) |
|:-|:-|:-|
| Key 0 | Switch Bluetooth connection (cycle through 1 → 2 → 3) | — |
| Key 1 | Left click | — |
| Key 2 | Middle click | Scroll + forward/back gesture layer |
| Key 3 | Right click | Window-management gesture layer |

**Key 0 + Key 3** (combo) clears the current Bluetooth pairing.

The trackball provides pointer movement (600 CPI, smart-mode enabled).

### Scroll & forward/back gestures (hold Key 2)

Hold **Key 2** to enter the scroll layer. The cursor stays still (the horizontal axis is
zeroed); move the trackball up/down to scroll, or flick left/right to trigger a forward/back
gesture (powered by [`zmk-mouse-gesture`](https://github.com/kot149/zmk-mouse-gesture)).
Bindings target Chrome on macOS:

| Trackball | Action |
|:-|:-|
| ↑ | Scroll down |
| ↓ | Scroll up |
| ← flick | Forward (⌘]) |
| → flick | Back (⌘[) |

Scroll is produced by `&zip_x_scaler 0 1` (zeroes the horizontal axis) feeding
`&zip_xy_to_scroll_mapper`, then `&zip_scroll_scaler (-1) 32` inverts and scales it. The
`-1` gives **macOS-style natural scrolling**: pushing the trackball up behaves like
swiping two fingers up on a trackpad (the page content follows your finger), so the view
scrolls down.

### Window-management gestures (hold Key 3)

Hold **Key 3** to enter the rectangle layer. All trackball movement is zeroed (the cursor
stays still); flick the trackball to trigger a macOS window-manager
([Rectangle.app](https://rectangleapp.com/)) shortcut:

| Trackball | Action | Shortcut |
|:-|:-|:-|
| ↑ flick | Maximize | ⌃⌥⏎ |
| ↓ flick | Restore | ⌃⌥⌫ |
| ← flick | Left third | ⌃⌥D |
| → flick | Right two-thirds | ⌃⌥T |

To change gestures, scrolling, or bindings, edit the `zip_scroll_gesture` (scroll +
forward/back) and `zip_rectangle_gesture` (window management) nodes and the `scroll` / `rectangle` blocks
under `&trackball_listener` in `config/boards/shields/kimi/kimiboard.keymap`.

## Building

This config pins its upstream dependencies (ZMK, `zmk-rgbled-widget`, and `zmk-mouse-gesture`) to fixed commits in `config/west.yml` for reproducible builds. See [Updating pinned versions](#updating-pinned-versions) to move to newer commits.

### GitHub Actions (CI)

Firmware is built automatically via GitHub Actions on push or pull request. Download the `.uf2` artifacts from the Actions run page.

Two firmware images are produced:
- **kimiboard** — main firmware with ZMK Studio support
- **settings_reset** — utility firmware to reset stored settings

### Local Build (macOS + colima + Dev Container)

Based on the ZMK [Container Setup](https://zmk.dev/docs/development/local-toolchain/setup/container) and [Build & Flash](https://zmk.dev/docs/development/build-flash) documentation.

#### Prerequisites

```bash
brew install colima docker devcontainer
```

#### Setup

First clone this repository, then read the pinned SHAs from its manifest into shell variables. The SHAs are the single source of truth and live as the `revision` values in `config/west.yml` (the `zmk`, `zmk-rgbled-widget`, and `zmk-mouse-gesture` projects):

```bash
git clone https://github.com/susumuota/zmk-config-KimiBoard.git

ZMK_REV=$(awk '/name: zmk$/{f=1} f&&/revision:/{print $2; exit}' zmk-config-KimiBoard/config/west.yml)
echo "ZMK_REV: $ZMK_REV"

RGBLED_REV=$(awk '/name: zmk-rgbled-widget/{f=1} f&&/revision:/{print $2; exit}' zmk-config-KimiBoard/config/west.yml)
echo "RGBLED_REV: $RGBLED_REV"

MOUSEGESTURE_REV=$(awk '/name: zmk-mouse-gesture/{f=1} f&&/revision:/{print $2; exit}' zmk-config-KimiBoard/config/west.yml)
echo "MOUSEGESTURE_REV: $MOUSEGESTURE_REV"
```

Then clone the ZMK firmware source and extra modules, checking out those same pinned commits so local builds match CI:

```bash
git clone https://github.com/zmkfirmware/zmk.git
cd zmk && git checkout "$ZMK_REV" && cd ..

mkdir -p zmk-modules
git clone https://github.com/caksoylar/zmk-rgbled-widget.git zmk-modules/zmk-rgbled-widget
cd zmk-modules/zmk-rgbled-widget && git checkout "$RGBLED_REV" && cd ../..

git clone https://github.com/kot149/zmk-mouse-gesture.git zmk-modules/zmk-mouse-gesture
cd zmk-modules/zmk-mouse-gesture && git checkout "$MOUSEGESTURE_REV" && cd ../..
```

Start colima and create Docker volumes to mount the config and modules into the container. The `colima start` flags allocate 2 CPUs (`-c 2`), 4GB RAM (`-m 4`), and a 100GB disk (`-d 100`), and use the macOS `vz` virtualization backend (`-t vz`).

```bash
colima start -c 2 -m 4 -d 100 -t vz

docker volume create --driver local -o o=bind -o type=none \
  -o device="$(pwd)/zmk-config-KimiBoard" zmk-config

docker volume create --driver local -o o=bind -o type=none \
  -o device="$(pwd)/zmk-modules" zmk-modules

docker volume ls
```

Start the Dev Container and open a shell:

```bash
devcontainer up --workspace-folder "$(pwd)/zmk"
docker ps -a

devcontainer exec --workspace-folder "$(pwd)/zmk" bash
```

Inside the container, initialize the Zephyr workspace:

```bash
west init -l app/
west update
```

#### Build

Run from the `app/` directory inside the container:

```bash
cd app
mkdir -p /workspaces/zmk-config/firmware
```

Main firmware:

```bash
west build -p -d build/main -b xiao_ble//zmk -- \
  -DSHIELD="kimiboard rgbled_adapter" \
  -DZMK_CONFIG="/workspaces/zmk-config/config" \
  -DZMK_EXTRA_MODULES="/workspaces/zmk-modules/zmk-rgbled-widget;/workspaces/zmk-modules/zmk-mouse-gesture" \
  -DSNIPPET=studio-rpc-usb-uart \
  -DCONFIG_ZMK_STUDIO=y \
  -DCONFIG_ZMK_STUDIO_LOCKING=n \
  && cp -p build/main/zephyr/zmk.uf2 \
    /workspaces/zmk-config/firmware/kimiboard_rgbled_adapter-xiao_ble__zmk-zmk.uf2
```

Settings reset firmware:

```bash
west build -p -d build/reset -b xiao_ble//zmk -- \
  -DSHIELD=settings_reset \
  -DZMK_CONFIG="/workspaces/zmk-config/config" \
  && cp -p build/reset/zephyr/zmk.uf2 \
    /workspaces/zmk-config/firmware/settings_reset-xiao_ble__zmk-zmk.uf2
```

#### Flash

Put the board into bootloader mode (double-tap reset), then from a separate terminal on the host. The `-X` flag is macOS only and prevents extended attribute errors with UF2 mass storage.

Flash the settings reset firmware first:

```bash
cp -X zmk-config-KimiBoard/firmware/settings_reset-xiao_ble__zmk-zmk.uf2 /Volumes/XIAO-SENSE/
```

Put the board into bootloader mode again, then flash the main firmware:

```bash
cp -X zmk-config-KimiBoard/firmware/kimiboard_rgbled_adapter-xiao_ble__zmk-zmk.uf2 /Volumes/XIAO-SENSE/
```

#### Cleanup

Stop the Dev Container and remove Docker volumes:

```bash
docker ps -a
docker stop <container_id>
docker rm <container_id>
docker ps -a
```

Remove Docker volumes created by the setup and the Dev Container:

```bash
docker volume ls
docker volume rm zmk-config zmk-modules \
  zmk-root-user zmk-zephyr zmk-zephyr-modules zmk-zephyr-tools
docker volume ls
```

Stop colima:

```bash
colima status
colima stop
colima status
```

To also delete the colima VM:

```bash
colima list
colima delete
colima list
```

### Updating pinned versions

To move the pinned dependencies to newer upstream commits:

1. Find the SHAs you want. For the latest `main` of each:

```bash
git ls-remote https://github.com/zmkfirmware/zmk.git refs/heads/main
git ls-remote https://github.com/caksoylar/zmk-rgbled-widget.git refs/heads/main
git ls-remote https://github.com/kot149/zmk-mouse-gesture.git refs/heads/v1
```

2. Update the three `revision` values in `config/west.yml`.
3. Update the workflow ref in `.github/workflows/build.yml` to the same SHA as the `zmk` revision — these must stay in sync.
4. Commit the changes.
