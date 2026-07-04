#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html.parser
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg", ".css", ".js", ".json"}
REQUIRED_ROUTES = [
    "/",
    "/services/",
    "/gallery/",
    "/about/",
    "/testimonials/",
    "/contact/",
    "/privacy-policy/",
    "/terms-of-use/",
]
CORE_LINKS = REQUIRED_ROUTES
TOKEN_RE = re.compile(r"__[A-Z0-9_]+__")
PLACEHOLDER_RE = re.compile(r"\[REPLACE_WITH_[A-Z0-9_]+\]")
LINK_ATTRS = {"href", "src", "action"}
SRCSET_SPLIT_RE = re.compile(r"\s*,\s*")


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if not value:
                continue
            if name in LINK_ATTRS:
                self.links.append((name, value))
            elif name == "srcset":
                for part in SRCSET_SPLIT_RE.split(value.strip()):
                    if not part:
                        continue
                    self.links.append((name, part.split()[0]))


def load_env_values(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        raise SystemExit(f"Env example file not found: {env_path}")

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def route_file(dist_dir: Path, route: str) -> Path:
    if route == "/":
        return dist_dir / "index.html"
    return dist_dir / route.strip("/") / "index.html"


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


def strip_base_path_for_local_target(url_path: str, base_path: str) -> str | None:
    if not base_path:
        return url_path or "/"
    if url_path == base_path:
        return "/"
    prefix = f"{base_path}/"
    if url_path.startswith(prefix):
        return "/" + url_path[len(prefix):]
    return None


def browser_path(route: str, base_path: str) -> str:
    if not base_path:
        return route
    if route == "/":
        return f"{base_path}/"
    return f"{base_path}{route}"


def text_files(dist_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in dist_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS
    )


def find_tokens(dist_dir: Path, allowed_placeholders: set[str]) -> tuple[list[str], dict[str, int]]:
    failures: list[str] = []
    allowed_counts = {placeholder: 0 for placeholder in sorted(allowed_placeholders)}

    for path in text_files(dist_dir):
        text = path.read_text(encoding="utf-8")
        for token in sorted(set(TOKEN_RE.findall(text))):
            failures.append(f"{path.relative_to(dist_dir)} contains unreplaced template token {token}")

        for placeholder in PLACEHOLDER_RE.findall(text):
            if placeholder in allowed_counts:
                allowed_counts[placeholder] += 1
            else:
                failures.append(
                    f"{path.relative_to(dist_dir)} contains unexpected placeholder {placeholder}"
                )

    return failures, allowed_counts


def check_required_routes(dist_dir: Path) -> list[str]:
    failures = []
    for route in REQUIRED_ROUTES:
        path = route_file(dist_dir, route)
        route_label = f"required route {route}"
        failures.extend(check_file(path, route_label))
    return failures


def check_file(path: Path, label: str) -> list[str]:
    if not path.exists():
        return [f"missing {label}: {path.name}"]
    if not path.is_file():
        return [f"{label} is not a file: {path.name}"]
    if path.stat().st_size == 0:
        return [f"{label} is empty: {path.name}"]
    return []


def check_sitemap(dist_dir: Path, site_url: str) -> list[str]:
    failures = check_file(dist_dir / "sitemap.xml", "sitemap")
    if failures:
        return failures

    sitemap = dist_dir / "sitemap.xml"
    try:
        root = ET.parse(sitemap).getroot()
    except ET.ParseError as exc:
        return [f"sitemap.xml is invalid XML: {exc}"]

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text or "" for node in root.findall("sm:url/sm:loc", namespace)]
    expected = [f"{site_url.rstrip('/')}{route}" for route in REQUIRED_ROUTES]
    missing = sorted(set(expected) - set(locs))
    extra = sorted(set(locs) - set(expected))
    failures.extend(f"sitemap.xml missing loc {loc}" for loc in missing)
    failures.extend(f"sitemap.xml has unexpected loc {loc}" for loc in extra)
    return failures


def check_robots(dist_dir: Path, site_url: str) -> list[str]:
    failures = check_file(dist_dir / "robots.txt", "robots.txt")
    if failures:
        return failures

    lines = [line.strip() for line in (dist_dir / "robots.txt").read_text(encoding="utf-8").splitlines()]
    directives = [line for line in lines if line and not line.startswith("#")]
    expected_sitemap = f"Sitemap: {site_url.rstrip('/')}/sitemap.xml"
    if "User-agent: *" not in directives:
        failures.append("robots.txt missing 'User-agent: *'")
    if "Allow: /" not in directives:
        failures.append("robots.txt missing 'Allow: /'")
    if expected_sitemap not in directives:
        failures.append(f"robots.txt missing '{expected_sitemap}'")
    return failures


def local_link_target_exists(dist_dir: Path, url: str, base_path: str) -> bool:
    parsed = urlparse(url)
    path = strip_base_path_for_local_target(parsed.path, base_path)
    if path is None:
        return False
    if not path or path == "/":
        return (dist_dir / "index.html").exists()
    if path.endswith("/"):
        return (dist_dir / path.strip("/") / "index.html").exists()
    return (dist_dir / path.lstrip("/")).exists()


def should_skip_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.netloc or (parsed.scheme and parsed.scheme != "file")) or url.startswith("#")


def check_links(dist_dir: Path, base_path: str) -> list[str]:
    failures: list[str] = []

    for html_path in sorted(dist_dir.rglob("*.html")):
        parser = LinkParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        page_hrefs: set[str] = set()
        for attr, url in parser.links:
            parsed = urlparse(url)
            if attr == "href":
                page_hrefs.add(parsed.path or url)
            if not url.startswith("/") or should_skip_url(url):
                continue
            if (
                base_path
                and parsed.path.startswith("/")
                and parsed.path != base_path
                and not parsed.path.startswith(f"{base_path}/")
            ):
                failures.append(
                    f"{html_path.relative_to(dist_dir)} references root-relative {attr} target {url} outside configured base path {base_path}"
                )
                continue
            if not local_link_target_exists(dist_dir, url, base_path):
                failures.append(
                    f"{html_path.relative_to(dist_dir)} references missing local {attr} target {url}"
                )

        expected_core_links = [browser_path(route, base_path) for route in CORE_LINKS]
        missing_core_links = [href for href in expected_core_links if href not in page_hrefs]
        failures.extend(
            f"{html_path.relative_to(dist_dir)} missing core link {href}"
            for href in missing_core_links
        )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify rendered EVOMTRS static assets.")
    parser.add_argument("dist", type=Path, help="Rendered site directory")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".env.example",
        help="Env example used to render and define allowed example placeholders",
    )
    args = parser.parse_args()

    dist_dir = args.dist.resolve()
    if not dist_dir.exists():
        print(f"FAIL: rendered directory not found: {dist_dir}", file=sys.stderr)
        return 1

    env_values = load_env_values(args.env_file)
    site_url = env_values.get("EVOMTRS_SITE_URL", "").rstrip("/")
    if not site_url:
        print("FAIL: EVOMTRS_SITE_URL missing from env example", file=sys.stderr)
        return 1
    base_path = normalize_public_base_path(
        site_url,
        env_values.get("EVOMTRS_PUBLIC_BASE_PATH"),
    )

    allowed_placeholders = {
        value for value in env_values.values() if PLACEHOLDER_RE.fullmatch(value)
    }

    failures: list[str] = []
    failures.extend(check_required_routes(dist_dir))
    failures.extend(check_sitemap(dist_dir, site_url))
    failures.extend(check_robots(dist_dir, site_url))
    failures.extend(check_links(dist_dir, base_path))
    token_failures, placeholder_counts = find_tokens(dist_dir, allowed_placeholders)
    failures.extend(token_failures)

    if failures:
        print("Static verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Verified rendered static site: {dist_dir}")
    print(f"Required routes: {len(REQUIRED_ROUTES)}")
    print("sitemap.xml: ok")
    print("robots.txt: ok")
    print("local links/assets: ok")
    print(f"public base path: {base_path or '/'}")
    print("unreplaced template tokens: none")
    if allowed_placeholders:
        print("allowed .env.example placeholders:")
        for placeholder, count in sorted(placeholder_counts.items()):
            print(f"- {placeholder}: {count} occurrence(s)")
    else:
        print("allowed .env.example placeholders: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
