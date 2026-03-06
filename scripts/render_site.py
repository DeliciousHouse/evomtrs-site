#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg"}


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def required_env() -> dict[str, str]:
    keys = [
        "EVOMTRS_SITE_URL",
        "EVOMTRS_BUSINESS_NAME",
        "EVOMTRS_CONTACT_EMAIL",
        "EVOMTRS_CONTACT_PHONE_E164",
        "EVOMTRS_CONTACT_PHONE_DISPLAY",
        "EVOMTRS_TEXT_PHONE_E164",
        "EVOMTRS_ADDRESS_LINE1",
        "EVOMTRS_CITY",
        "EVOMTRS_STATE",
        "EVOMTRS_ZIP",
        "EVOMTRS_PRICE_RANGE",
        "EVOMTRS_FOUNDER_NAME",
        "EVOMTRS_FOUNDER_ROLE",
        "EVOMTRS_FOUNDER_CREDENTIAL",
        "EVOMTRS_FORM_ENDPOINT",
        "EVOMTRS_LEGAL_UPDATED_DATE",
        "EVOMTRS_DIRECTIONS_URL",
        "EVOMTRS_MAP_EMBED_URL",
    ]
    missing = [key for key in keys if not os.environ.get(key)]
    if missing:
        raise SystemExit(f"Missing required env values: {', '.join(missing)}")

    site_url = os.environ["EVOMTRS_SITE_URL"].rstrip("/")
    full_address = ", ".join(
        part
        for part in [
            os.environ["EVOMTRS_ADDRESS_LINE1"],
            os.environ["EVOMTRS_CITY"],
            os.environ["EVOMTRS_STATE"],
            os.environ["EVOMTRS_ZIP"],
        ]
        if part
    )

    values = {key: os.environ[key] for key in keys}
    values["EVOMTRS_SITE_URL"] = site_url
    values["EVOMTRS_FULL_ADDRESS"] = full_address
    return values


def render_templates(src_dir: Path, out_dir: Path, values: dict[str, str]) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path in src_dir.rglob("*"):
        relative = path.relative_to(src_dir)
        target = out_dir / relative

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if path.suffix in TEXT_EXTENSIONS:
            text = path.read_text(encoding="utf-8")
            for key, value in values.items():
                text = text.replace(f"__{key}__", value)
            target.write_text(text, encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render EVOMTRS static site templates.")
    parser.add_argument("src", type=Path, help="Template source directory")
    parser.add_argument("out", type=Path, help="Output directory")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".env",
        help="Path to dotenv-style file",
    )
    args = parser.parse_args()

    load_env_file(args.env_file)
    values = required_env()
    render_templates(args.src, args.out, values)
    print(f"Rendered {args.src} -> {args.out}")


if __name__ == "__main__":
    main()
