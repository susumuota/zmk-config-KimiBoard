# ZMK Config for KimiBoard

<img width="1920" height="1080" alt="KimiBoard switches" src="https://github.com/user-attachments/assets/21cd87cc-cafe-45ed-b6bb-a46061c3a2e3" />

A 4-key Bluetooth/USB keyboard with a PMW3610 trackball, built on the Seeed XIAO BLE (nRF52840). Supports up to 3 Bluetooth pairings and includes an RGB LED status widget.

[ZMK Studio](https://zmk.studio/) is enabled, allowing keymap customization without reflashing.

## Default Keymap

| Key | Assignment |
|:-|:-|
| Key 0 | Switch Bluetooth connection (cycle through 1 → 2 → 3) |
| Key 1 | Left click |
| Key 2 | Hold: gesture layer |
| Key 3 | Right click |
| Key 0 + Key 3 | Clear current Bluetooth pairing |

The trackball provides pointer movement (400 CPI, smart-mode enabled).

### Gesture Layer (hold Key 2)

Hold **Key 2** and flick the trackball left or right to trigger a browser gesture
(powered by [`zmk-mouse-gesture`](https://github.com/kot149/zmk-mouse-gesture)), or move
it up/down to scroll. The cursor stays still while held (movement is converted to scroll
or zeroed). Key 2 is hold-only; it sends no middle click. Bindings target Chrome on
macOS:

| Trackball | Action |
|:-|:-|
| ← | Forward (⌘]) |
| → | Back (⌘[) |
| ↑ / ↓ | Scroll up / down |

Vertical scroll comes from `&zip_x_scaler 0 1` (zeroes the horizontal axis) feeding
`&zip_xy_to_scroll_mapper`, so only up/down scrolls. Edit the `&zip_mouse_gesture` node
and the `&trackball_listener` `gesture` block in
`config/boards/shields/kimi/kimiboard.keymap` to change gestures, scrolling, or bindings.

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
