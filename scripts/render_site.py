#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg"}


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return (
        not stripped
        or stripped.startswith("[REPLACE_WITH_")
        or stripped.startswith("__EVOMTRS_")
    )


def is_placeholder_phone(value: str) -> bool:
    stripped = value.strip()
    digits = "".join(ch for ch in stripped if ch.isdigit())
    return is_placeholder(stripped) or "*" in stripped or digits.endswith("0000")


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
    address_line1 = os.environ["EVOMTRS_ADDRESS_LINE1"]
    zip_code = os.environ["EVOMTRS_ZIP"]
    city = os.environ["EVOMTRS_CITY"]
    state = os.environ["EVOMTRS_STATE"]
    form_endpoint = os.environ["EVOMTRS_FORM_ENDPOINT"]
    phone_e164 = os.environ["EVOMTRS_CONTACT_PHONE_E164"]
    phone_display = os.environ["EVOMTRS_CONTACT_PHONE_DISPLAY"]
    text_phone_e164 = os.environ["EVOMTRS_TEXT_PHONE_E164"]

    has_placeholder_address = is_placeholder(address_line1) or is_placeholder(zip_code)
    has_placeholder_form_endpoint = is_placeholder(form_endpoint)
    has_placeholder_phone = is_placeholder_phone(phone_e164) or is_placeholder_phone(phone_display)

    address_parts = [
        "" if is_placeholder(address_line1) else address_line1,
        city,
        state,
        "" if is_placeholder(zip_code) else zip_code,
    ]
    full_address = ", ".join(part for part in address_parts if part)
    if has_placeholder_address:
        full_address = f"{city}, {state} service area. Shop address pending owner approval; visits by appointment."

    values = {key: os.environ[key] for key in keys}
    values["EVOMTRS_SITE_URL"] = site_url
    values["EVOMTRS_FULL_ADDRESS"] = full_address
    values["EVOMTRS_ADDRESS_LINE1"] = "" if is_placeholder(address_line1) else address_line1
    values["EVOMTRS_ZIP"] = "" if is_placeholder(zip_code) else zip_code
    values["EVOMTRS_SCHEMA_TELEPHONE"] = "" if has_placeholder_phone else phone_e164
    values["EVOMTRS_CONTACT_PHONE_E164"] = phone_e164
    values["EVOMTRS_TEXT_PHONE_E164"] = text_phone_e164
    values["EVOMTRS_CONTACT_PHONE_HREF"] = "#contact-phone-pending" if has_placeholder_phone else f"tel:{phone_e164}"
    values["EVOMTRS_TEXT_PHONE_HREF"] = "#contact-phone-pending" if has_placeholder_phone else f"sms:{text_phone_e164}"
    values["EVOMTRS_CONTACT_PHONE_DISPLAY"] = "Phone pending owner approval" if has_placeholder_phone else phone_display
    values["EVOMTRS_CONTACT_ACTION_CLASS"] = "contact-actions contact-actions--pending-phone" if has_placeholder_phone else "contact-actions"
    values["EVOMTRS_MOBILE_CTA_CLASS"] = "mobile-cta mobile-cta--pending-phone" if has_placeholder_phone else "mobile-cta"
    values["EVOMTRS_INTAKE_NOTICE"] = (
        '<p class="intake-notice" data-intake-placeholder>Online intake is not live in this preview build. Use the details below once the owner-approved phone is published, or email to start.</p>'
        if has_placeholder_form_endpoint
        else ""
    )
    values["EVOMTRS_INTAKE_LEAD"] = (
        "Online intake is not live in this preview build. Prepare vehicle details here, then use the owner-approved contact path when published."
        if has_placeholder_form_endpoint
        else "Call, text, or submit the form below. New intake submissions receive a reply within one business day."
    )
    values["EVOMTRS_INTAKE_HELP_TEXT"] = (
        "Online submission is not live in this preview build. Save these details and use the published contact path once owner-approved phone is available."
        if has_placeholder_form_endpoint
        else "Attach images of the vehicle or issue if helpful. If online submission is unavailable, use call/text and mention that photos are ready."
    )
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
