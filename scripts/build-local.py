#!/usr/bin/env python3
"""Build local ZMK firmware artifacts from build.yaml."""

import argparse
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


DEFAULT_ROOT = Path("/workspaces/zmk-config")
DEFAULT_ZMK_APP = Path("/workspaces/zmk/app")
DEFAULT_EXTRA_MODULES = "/workspaces/zmk-modules/zmk-rgbled-widget;/workspaces/zmk-modules/zmk-mouse-gesture"


def load_build_matrix(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or not isinstance(data.get("include"), list):
        raise SystemExit(f"{path} must contain an include list")

    entries = data["include"]
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("board"):
            raise SystemExit(f"{path} contains a build entry without board")

    return entries


def default_artifact_name(entry: dict[str, Any]) -> str:
    board = str(entry["board"]).replace("/", "_")
    shield = str(entry.get("shield") or "")
    # This differs from GitHub Actions, which preserves spaces in artifact names.
    shield = shield.replace(" ", "_")
    return f"{shield + '-' if shield else ''}{board}-zmk"


def build_command(
    entry: dict[str, Any],
    *,
    zmk_app: Path,
    config_dir: Path,
    build_dir: Path,
    extra_modules: str,
) -> list[str]:
    cmd = [
        "west",
        "build",
        "-p",
        "-s",
        str(zmk_app),
        "-d",
        str(build_dir),
        "-b",
        str(entry["board"]),
    ]

    if snippet := entry.get("snippet"):
        cmd.extend(["-S", str(snippet)])

    cmd.extend(
        [
            "--",
            f"-DZMK_CONFIG={config_dir}",
        ]
    )

    if shield := entry.get("shield"):
        cmd.append(f"-DSHIELD={shield}")

    if extra_modules:
        cmd.append(f"-DZMK_EXTRA_MODULES={extra_modules}")

    if cmake_args := entry.get("cmake-args"):
        cmd.extend(shlex.split(str(cmake_args)))

    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local ZMK firmware artifacts from build.yaml.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--zmk-app", type=Path, default=DEFAULT_ZMK_APP)
    parser.add_argument("--extra-modules", default=DEFAULT_EXTRA_MODULES)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    build_yaml = args.root / "build.yaml"
    config_dir = args.root / "config"
    output_dir = args.root / "firmware"
    entries = load_build_matrix(build_yaml)

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        artifact_name = str(entry.get("artifact-name") or default_artifact_name(entry))
        build_dir = args.zmk_app / "build" / "local" / artifact_name
        dest = output_dir / f"{artifact_name}.uf2"

        cmd = build_command(
            entry,
            zmk_app=args.zmk_app,
            config_dir=config_dir,
            build_dir=build_dir,
            extra_modules=args.extra_modules,
        )

        print("+ " + shlex.join(cmd))

        if args.dry_run:
            print(f"would write {dest}")
            continue

        subprocess.run(cmd, check=True)

        uf2 = build_dir / "zephyr" / "zmk.uf2"
        if not uf2.is_file():
            raise SystemExit(f"missing build output: {uf2}")

        shutil.copy2(uf2, dest)
        print(f"wrote {dest}")


if __name__ == "__main__":
    main()
