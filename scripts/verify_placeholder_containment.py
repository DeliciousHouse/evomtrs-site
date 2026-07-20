#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".html", ".xml", ".txt", ".svg", ".css", ".js", ".json"}
PUBLIC_ROUTES = [
    "index.html",
    "services/index.html",
    "gallery/index.html",
    "about/index.html",
    "testimonials/index.html",
    "contact/index.html",
    "privacy-policy/index.html",
    "terms-of-use/index.html",
]
DISALLOWED_MARKERS = [
    "Phone pending owner approval",
    "hidconsult",
    "support@hidconsult.com",
    "[REPLACE_WITH_",
    "__EVOMTRS_",
]
HOLDING_MARKER = "data-evomtrs-holding=\"owner-values-pending\""
NOINDEX_MARKER = '<meta name="robots" content="noindex, nofollow" />'


def text_files(dist_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in dist_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify owner-pending production-looking EVOMTRS builds are contained."
    )
    parser.add_argument("dist", type=Path, help="Rendered site directory")
    parser.add_argument(
        "--expect-canonical-root",
        help="Optional expected canonical URL for the rendered root route.",
    )
    parser.add_argument(
        "--expect-escaped-business-name",
        help="Optional escaped business name expected in holding-page metadata.",
    )
    args = parser.parse_args()

    dist_dir = args.dist.resolve()
    failures: list[str] = []
    if not dist_dir.exists():
        failures.append(f"rendered directory not found: {dist_dir}")
    else:
        for route in PUBLIC_ROUTES:
            path = dist_dir / route
            if not path.is_file():
                failures.append(f"missing public route: {route}")
                continue
            html = path.read_text(encoding="utf-8")
            if HOLDING_MARKER not in html:
                failures.append(f"{route} is not in owner-values-pending holding state")
            if NOINDEX_MARKER not in html:
                failures.append(f"{route} is missing noindex/nofollow robots meta")

            if route == "index.html" and args.expect_canonical_root:
                canonical = f'<link rel="canonical" href="{args.expect_canonical_root}" />'
                if canonical not in html:
                    failures.append(
                        f"{route} canonical did not match {args.expect_canonical_root!r}"
                    )

            if route == "index.html" and args.expect_escaped_business_name:
                expected_description = (
                    f'<meta name="description" content="{args.expect_escaped_business_name} '
                    "public launch details are being verified before intake details are published."
                    '" />'
                )
                if expected_description not in html:
                    failures.append("root holding meta description does not contain escaped business name")

        robots = dist_dir / "robots.txt"
        if not robots.is_file():
            failures.append("missing robots.txt")
        else:
            robots_text = robots.read_text(encoding="utf-8")
            if "Disallow: /" not in robots_text:
                failures.append("robots.txt does not disallow crawlers for holding build")

        for path in text_files(dist_dir):
            text = path.read_text(encoding="utf-8")
            for marker in DISALLOWED_MARKERS:
                if marker.lower() in text.lower():
                    failures.append(f"{path.relative_to(dist_dir)} contains disallowed marker {marker!r}")

    if failures:
        print("Placeholder containment verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Verified placeholder containment: {dist_dir}")
    print(f"Public routes in holding state: {len(PUBLIC_ROUTES)}")
    print("Known placeholder markers: none")
    print("robots.txt: Disallow: /")
    print("meta robots: noindex, nofollow")
    if args.expect_canonical_root:
        print(f"canonical root: {args.expect_canonical_root}")
    if args.expect_escaped_business_name:
        print("business name escaping: verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())