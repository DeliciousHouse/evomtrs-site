#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse


TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg"}
PREVIEW_PLACEHOLDER_FLAG = "EVOMTRS_ALLOW_PREVIEW_PLACEHOLDERS"
HOLDING_ROUTES = {
    Path("index.html"): "/",
    Path("services/index.html"): "/services/",
    Path("gallery/index.html"): "/gallery/",
    Path("about/index.html"): "/about/",
    Path("testimonials/index.html"): "/testimonials/",
    Path("contact/index.html"): "/contact/",
    Path("privacy-policy/index.html"): "/privacy-policy/",
    Path("terms-of-use/index.html"): "/terms-of-use/",
}


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


def normalize_public_base_path(site_url: str, override: str | None = None) -> str:
    raw_path = (override or "").strip()
    if not raw_path:
        raw_path = urlparse(site_url).path
    raw_path = raw_path.strip()
    if raw_path in {"", "/"}:
        return ""
    if "://" in raw_path or "?" in raw_path or "#" in raw_path:
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH: {raw_path!r}")
    trimmed_path = raw_path
    if trimmed_path.startswith("/"):
        trimmed_path = trimmed_path[1:]
    if trimmed_path.endswith("/"):
        trimmed_path = trimmed_path[:-1]
    if not trimmed_path:
        return ""
    parts = trimmed_path.split("/")
    if any(not part for part in parts):
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH duplicate slash: {raw_path!r}")
    if any(part == ".." for part in parts):
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH traversal segment: {raw_path!r}")
    return "/" + "/".join(parts)


def truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def is_production_looking_url(site_url: str) -> bool:
    parsed = urlparse(site_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host:
        return False
    return host not in {"localhost", "127.0.0.1", "::1"} and not host.endswith(".invalid")


def browser_path(route: str, base_path: str) -> str:
    if not base_path:
        return route
    if route == "/":
        return f"{base_path}/"
    return f"{base_path}{route}"


def route_url(site_url: str, route: str, base_path: str) -> str:
    parsed = urlparse(site_url)
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else site_url.rstrip("/")
    return f"{origin}{browser_path(route, base_path)}"


def render_holding_page(route: str, values: dict[str, str]) -> str:
    site_url = values["EVOMTRS_SITE_URL"]
    base_path = values["EVOMTRS_BASE_PATH"]
    business_name = html.escape(values["EVOMTRS_BUSINESS_NAME"], quote=True)
    canonical = html.escape(route_url(site_url, route, base_path), quote=True)
    nav = "\n".join(
        f'        <a href="{html.escape(browser_path(item, base_path), quote=True)}">{label}</a>'
        for item, label in [
            ("/", "Home"),
            ("/services/", "Services"),
            ("/gallery/", "Case Studies"),
            ("/about/", "About"),
            ("/testimonials/", "Proof"),
            ("/contact/", "Contact"),
            ("/privacy-policy/", "Privacy Policy"),
            ("/terms-of-use/", "Terms of Use"),
        ]
    )
    css_href = html.escape(f"{base_path}/assets/css/styles.min.css" if base_path else "/assets/css/styles.min.css", quote=True)
    favicon_svg = html.escape(f"{base_path}/favicon.svg" if base_path else "/favicon.svg", quote=True)
    favicon_ico = html.escape(f"{base_path}/favicon.ico" if base_path else "/favicon.ico", quote=True)
    return f"""<!doctype html>
<html lang="en" data-evomtrs-holding="owner-values-pending">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex, nofollow" />
  <title>{business_name} | Site update in progress</title>
  <meta name="description" content="{business_name} public launch details are being verified before intake details are published." />
  <link rel="canonical" href="{canonical}" />
  <link rel="icon" type="image/svg+xml" href="{favicon_svg}" />
  <link rel="icon" href="{favicon_ico}" sizes="any" />
  <link rel="stylesheet" href="{css_href}" />
</head>
<body>
  <main class="section" id="main">
    <div class="container" style="max-width: 760px; padding-top: 12vh; padding-bottom: 12vh;">
      <p class="kicker">Site update</p>
      <h1>{business_name} public launch details are being verified.</h1>
      <p class="lead">This holding build intentionally withholds intake, phone, visit, and proof details until owner-approved launch values are configured.</p>
      <p class="small">No customer intake path is live from this build. Check back after the approved GitHub Pages launch.</p>
      <nav class="footer-links" aria-label="Site routes">
{nav}
      </nav>
    </div>
  </main>
</body>
</html>
"""


def render_holding_robots(site_url: str, base_path: str) -> str:
    return f"User-agent: *\nDisallow: /\n\nSitemap: {route_url(site_url, '/sitemap.xml', base_path)}\n"


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
    base_path = normalize_public_base_path(
        site_url,
        os.environ.get("EVOMTRS_PUBLIC_BASE_PATH"),
    )
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
    owner_values_pending = has_placeholder_address or has_placeholder_form_endpoint or has_placeholder_phone

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
    values["EVOMTRS_BASE_PATH"] = base_path
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
    values["EVOMTRS_CONTAIN_OWNER_PENDING_PLACEHOLDERS"] = (
        "1"
        if owner_values_pending and is_production_looking_url(site_url) and not truthy_env(PREVIEW_PLACEHOLDER_FLAG)
        else ""
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
            if values.get("EVOMTRS_CONTAIN_OWNER_PENDING_PLACEHOLDERS") and relative in HOLDING_ROUTES:
                target.write_text(render_holding_page(HOLDING_ROUTES[relative], values), encoding="utf-8")
                continue

            text = path.read_text(encoding="utf-8")
            for key, value in values.items():
                text = text.replace(f"__{key}__", value)
            if values.get("EVOMTRS_CONTAIN_OWNER_PENDING_PLACEHOLDERS") and relative == Path("robots.txt"):
                text = render_holding_robots(values["EVOMTRS_SITE_URL"], values["EVOMTRS_BASE_PATH"])
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
