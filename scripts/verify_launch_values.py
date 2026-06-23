#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html.parser
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

ENDPOINT_KEY = "EVOMTRS_FORM_ENDPOINT"
REDACTED_ENDPOINT = f"{ENDPOINT_KEY}=[REDACTED]"
TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg", ".css", ".js", ".json"}
PLACEHOLDER_RE = re.compile(r"\[REPLACE_WITH_[A-Z0-9_]+\]")
TEMPLATE_RE = re.compile(r"__EVOMTRS_[A-Z0-9_]+__")
URLISH_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)

PUBLIC_KEYS = [
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
    "EVOMTRS_LEGAL_UPDATED_DATE",
    "EVOMTRS_DIRECTIONS_URL",
    "EVOMTRS_MAP_EMBED_URL",
]
REQUIRED_KEYS = PUBLIC_KEYS + [ENDPOINT_KEY]


@dataclass(frozen=True)
class Check:
    row: str
    passed: bool
    evidence: str
    next_owner: str


class AttributeParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attrs: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is not None:
                self.attrs.append((tag, name, value))


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


def load_env_values(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        raise SystemExit(f"Env file not found: {env_path}")

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def rendered_files(dist_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(dist_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            files[str(path.relative_to(dist_dir))] = path.read_text(encoding="utf-8")
    return files


def require_keys(values: dict[str, str]) -> list[str]:
    missing = [key for key in REQUIRED_KEYS if not values.get(key)]
    return [f"missing env value {key}" for key in missing]


def contains_any(files: dict[str, str], needle: str, paths: list[str] | None = None) -> bool:
    selected = paths or list(files)
    return any(needle in files.get(path, "") for path in selected)


def file_contains(files: dict[str, str], path: str, needle: str) -> bool:
    return needle in files.get(path, "")


def attr_values(files: dict[str, str], path: str, tag: str, attr: str) -> list[str]:
    parser = AttributeParser()
    parser.feed(files.get(path, ""))
    return [value for parsed_tag, parsed_attr, value in parser.attrs if parsed_tag == tag and parsed_attr == attr]


def local_route_files(files: dict[str, str]) -> list[str]:
    return sorted(path for path in files if path.endswith("index.html"))


def safe_endpoint_label(value: str) -> str:
    if is_placeholder(value):
        return f"{ENDPOINT_KEY}=[REPLACE_WITH_FORM_ENDPOINT]"
    return REDACTED_ENDPOINT


def endpoint_leaked(files: dict[str, str], endpoint: str) -> bool:
    if is_placeholder(endpoint):
        return False
    for path, text in files.items():
        if path == "contact/index.html":
            text = text.replace(f'action="{endpoint}"', 'action="[EXPECTED_REDACTED_FORM_ENDPOINT]"')
            text = text.replace(f"action='{endpoint}'", "action='[EXPECTED_REDACTED_FORM_ENDPOINT]'")
        if endpoint in text:
            return True
    return False


def format_check(row: str, passed: bool, evidence: str, next_owner: str) -> Check:
    return Check(row=row, passed=passed, evidence=evidence, next_owner=next_owner)


def run_checks(dist_dir: Path, values: dict[str, str], files: dict[str, str]) -> tuple[list[Check], list[str]]:
    failures: list[str] = []
    failures.extend(require_keys(values))

    endpoint = values.get(ENDPOINT_KEY, "")
    if endpoint_leaked(files, endpoint):
        failures.append(f"raw {ENDPOINT_KEY} value is present in rendered output")

    unexpected_tokens = []
    for path, text in files.items():
        unexpected_tokens.extend(f"{path}: {token}" for token in sorted(set(TEMPLATE_RE.findall(text))))
    if unexpected_tokens:
        failures.append("unreplaced EVOMTRS template token(s): " + "; ".join(unexpected_tokens))

    allowed_placeholders = {value for value in values.values() if PLACEHOLDER_RE.fullmatch(value)}
    unexpected_placeholders = []
    for path, text in files.items():
        for placeholder in sorted(set(PLACEHOLDER_RE.findall(text))):
            if placeholder not in allowed_placeholders:
                unexpected_placeholders.append(f"{path}: {placeholder}")
    if unexpected_placeholders:
        failures.append("unexpected replacement placeholder(s): " + "; ".join(unexpected_placeholders))

    site_url = values.get("EVOMTRS_SITE_URL", "").rstrip("/")
    business_name = values.get("EVOMTRS_BUSINESS_NAME", "")
    email = values.get("EVOMTRS_CONTACT_EMAIL", "")
    phone_e164 = values.get("EVOMTRS_CONTACT_PHONE_E164", "")
    phone_display = values.get("EVOMTRS_CONTACT_PHONE_DISPLAY", "")
    text_phone = values.get("EVOMTRS_TEXT_PHONE_E164", "")
    address_line1 = values.get("EVOMTRS_ADDRESS_LINE1", "")
    city = values.get("EVOMTRS_CITY", "")
    state = values.get("EVOMTRS_STATE", "")
    zip_code = values.get("EVOMTRS_ZIP", "")
    directions_url = values.get("EVOMTRS_DIRECTIONS_URL", "")
    map_url = values.get("EVOMTRS_MAP_EMBED_URL", "")
    price_range = values.get("EVOMTRS_PRICE_RANGE", "")
    founder_name = values.get("EVOMTRS_FOUNDER_NAME", "")
    founder_role = values.get("EVOMTRS_FOUNDER_ROLE", "")
    founder_credential = values.get("EVOMTRS_FOUNDER_CREDENTIAL", "")
    legal_date = values.get("EVOMTRS_LEGAL_UPDATED_DATE", "")

    has_placeholder_phone = is_placeholder_phone(phone_e164) or is_placeholder_phone(phone_display)
    has_placeholder_address = is_placeholder(address_line1) or is_placeholder(zip_code)
    has_placeholder_endpoint = is_placeholder(endpoint)

    checks = [
        format_check(
            "Domain: EVOMTRS_SITE_URL",
            bool(site_url and file_contains(files, "sitemap.xml", f"{site_url}/") and file_contains(files, "robots.txt", f"Sitemap: {site_url}/sitemap.xml") and contains_any(files, f'canonical" href="{site_url}/')),
            "canonical links, sitemap.xml, and robots.txt point at EVOMTRS_SITE_URL",
            "Brendan hard gate then dept-devops",
        ),
        format_check(
            "Contact: EVOMTRS_BUSINESS_NAME",
            bool(business_name and contains_any(files, f'"name": "{business_name}"', ["index.html"])),
            "homepage structured data name matches EVOMTRS_BUSINESS_NAME",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Contact: EVOMTRS_CONTACT_EMAIL",
            bool(email and contains_any(files, f"mailto:{email}")),
            "mailto links and legal contacts use EVOMTRS_CONTACT_EMAIL",
            "dept-devops",
        ),
        format_check(
            "Contact: EVOMTRS_CONTACT_PHONE_E164 / DISPLAY",
            bool(
                (has_placeholder_phone and contains_any(files, "Phone pending owner approval") and contains_any(files, "#contact-phone-pending"))
                or ((not has_placeholder_phone) and contains_any(files, f"tel:{phone_e164}") and contains_any(files, phone_display))
            ),
            "phone renders as pending fallback for placeholder values, or as matching tel/display values after approval",
            "dept-devops",
        ),
        format_check(
            "SMS: EVOMTRS_TEXT_PHONE_E164",
            bool(
                (has_placeholder_phone and contains_any(files, "#contact-phone-pending"))
                or ((not has_placeholder_phone) and contains_any(files, f"sms:{text_phone}"))
            ),
            "SMS CTA uses pending fallback for placeholder phone, or sms: link after approval",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Location/map: street address publish policy",
            bool(
                (has_placeholder_address and contains_any(files, f"{city}, {state} service area. Shop address pending owner approval; visits by appointment."))
                or ((not has_placeholder_address) and contains_any(files, address_line1) and contains_any(files, zip_code))
            ),
            "visible address uses service-area fallback for placeholder address, or approved street/ZIP after approval",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Location/map: EVOMTRS_DIRECTIONS_URL",
            bool(directions_url and any(directions_url in value for value in attr_values(files, "index.html", "a", "href") + attr_values(files, "contact/index.html", "a", "href"))),
            "directions CTA hrefs use EVOMTRS_DIRECTIONS_URL",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Location/map: EVOMTRS_MAP_EMBED_URL",
            bool(map_url and any(map_url in value for value in attr_values(files, "index.html", "iframe", "src") + attr_values(files, "contact/index.html", "iframe", "src"))),
            "home/contact map iframe src values use EVOMTRS_MAP_EMBED_URL",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Location/map: service area and EVOMTRS_PRICE_RANGE",
            bool(price_range and contains_any(files, f'"priceRange": "{price_range}"') and contains_any(files, "Jacksonville, Ponte Vedra, Amelia Island, St. Johns, North Florida")),
            "structured data price range and visible service-area copy are present",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Form: provider/backend name",
            True,
            "not rendered locally; record provider readiness in owner-answer checklist without secrets",
            "dept-product",
        ),
        format_check(
            "Form: EVOMTRS_FORM_ENDPOINT",
            bool(
                (has_placeholder_endpoint and any("[REPLACE_WITH_FORM_ENDPOINT]" in value for value in attr_values(files, "contact/index.html", "form", "action")))
                or ((not has_placeholder_endpoint) and any(endpoint == value for value in attr_values(files, "contact/index.html", "form", "action")) and not endpoint_leaked(files, endpoint))
            ),
            f"contact form action evidence: {safe_endpoint_label(endpoint)}; raw value not printed by this script",
            "Brendan hard gate then dept-devops",
        ),
        format_check(
            "Form: multipart readiness and spam controls",
            bool(file_contains(files, "contact/index.html", 'enctype="multipart/form-data"') and file_contains(files, "contact/index.html", 'name="vehicle_photos"')),
            "contact form is multipart and includes optional vehicle_photos input; spam readiness remains owner/provider approval",
            "dept-product then dept-devops/QA",
        ),
        format_check(
            "Form: fallback policy if endpoint is not ready",
            bool(
                (has_placeholder_endpoint and file_contains(files, "contact/index.html", "Online intake is not live in this preview build") and file_contains(files, "contact/index.html", "Call instead"))
                or ((not has_placeholder_endpoint) and file_contains(files, "contact/index.html", "Call, text, or submit the form below"))
            ),
            "contact page shows non-live fallback for placeholder endpoint, or live-intake copy after endpoint approval",
            "dept-eng then dept-qa",
        ),
        format_check(
            "Legal: Privacy Policy approval",
            bool(file_contains(files, "privacy-policy/index.html", "Privacy Policy") and file_contains(files, "privacy-policy/index.html", legal_date)),
            "privacy policy renders with EVOMTRS_LEGAL_UPDATED_DATE",
            "Brendan hard gate if legal commitment, otherwise dept-eng",
        ),
        format_check(
            "Legal: Terms of Use approval",
            bool(file_contains(files, "terms-of-use/index.html", "Terms of Use") and file_contains(files, "terms-of-use/index.html", legal_date)),
            "terms page renders with EVOMTRS_LEGAL_UPDATED_DATE",
            "Brendan hard gate if legal commitment, otherwise dept-eng",
        ),
        format_check(
            "Legal: EVOMTRS_LEGAL_UPDATED_DATE",
            bool(legal_date and contains_any(files, f"Last updated: {legal_date}", ["privacy-policy/index.html", "terms-of-use/index.html"])),
            "both legal pages show the configured legal updated date",
            "dept-devops",
        ),
        format_check(
            "Proof/claims: founder name, role, credential",
            bool(founder_name and founder_role and founder_credential and contains_any(files, founder_name, ["index.html", "about/index.html"]) and contains_any(files, founder_role, ["index.html", "about/index.html"]) and contains_any(files, founder_credential, ["index.html", "about/index.html"])),
            "home/about render founder identity and credential fields",
            "dept-devops or dept-eng",
        ),
        format_check(
            "Proof/claims: A.L., M.R., J.T. dossiers/assets",
            bool(all(contains_any(files, value, ["index.html", "testimonials/index.html"]) for value in ["A.L.", "M.R.", "J.T.", "Owner outcomes", "Owner outcome dossiers"])),
            "home/proof pages contain the three visible proof dossiers for owner approval review",
            "dept-eng then dept-qa",
        ),
        format_check(
            "Proof/claims: Mercedes/AMG-only positioning",
            bool(all(file_contains(files, path, "Mercedes") for path in local_route_files(files)) and contains_any(files, "Mercedes / AMG only")),
            "required routes retain Mercedes/AMG positioning for owner approval review",
            "dept-eng then dept-qa",
        ),
        format_check(
            "Proof/claims: one-business-day response promise",
            bool(contains_any(files, "one business day")),
            "contact/home copy includes the response-time promise for owner approval review",
            "dept-eng then dept-qa",
        ),
        format_check(
            "Dispatch: first manual GitHub Pages dispatch from main",
            True,
            "not a local-render check; remains blocked until explicit owner/Brendan approval after setup",
            "Brendan hard gate then dept-devops",
        ),
        format_check(
            "Rollback: smoke owner, rollback owner, launch-window contact path",
            True,
            "not a local-render check; must be recorded before any approved dispatch",
            "Brendan hard gate then dept-devops/QA",
        ),
    ]

    return checks, failures


def redact(text: str, endpoint: str) -> str:
    if endpoint and not is_placeholder(endpoint):
        text = text.replace(endpoint, REDACTED_ENDPOINT)
    return text


def print_report(checks: list[Check], failures: list[str], endpoint: str) -> None:
    passed = [check for check in checks if check.passed]
    failed = [check for check in checks if not check.passed]

    print("Launch-state value smoke matrix")
    print(f"Rows checked: {len(checks)}")
    print(f"Rows passing: {len(passed)}")
    print(f"Rows failing: {len(failed)}")
    print("Hard gates: local green does not authorize GitHub settings, variables, secrets, DNS, legal commitments, workflow dispatch, deploy, or production traffic.")
    print(f"Secret evidence contract: {REDACTED_ENDPOINT} only; raw endpoint is never printed.")
    print("")

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"[{status}] {check.row}")
        print(f"  evidence: {redact(check.evidence, endpoint)}")
        print(f"  next owner if failed: {check.next_owner}")

    if failures:
        print("", file=sys.stderr)
        print("Launch-value verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {redact(failure, endpoint)}", file=sys.stderr)
    if failed:
        print("", file=sys.stderr)
        print("Failing matrix rows:", file=sys.stderr)
        for check in failed:
            print(f"- {check.row}: {redact(check.evidence, endpoint)}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify EVOMTRS launch-state values in a rendered static site.")
    parser.add_argument("dist", type=Path, help="Rendered site directory")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".env.example",
        help="Dotenv-style file used to render the site",
    )
    args = parser.parse_args()

    dist_dir = args.dist.resolve()
    if not dist_dir.exists():
        print(f"FAIL: rendered directory not found: {dist_dir}", file=sys.stderr)
        return 1

    values = load_env_values(args.env_file)
    files = rendered_files(dist_dir)
    checks, failures = run_checks(dist_dir, values, files)
    endpoint = values.get(ENDPOINT_KEY, "")
    print_report(checks, failures, endpoint)

    if failures or any(not check.passed for check in checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
