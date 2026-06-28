#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_JSON = ROOT / "package.json"
README = ROOT / "README.md"
RUNBOOK = ROOT / "docs" / "github-pages-runbook.md"
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-github-pages.yml"

WRANGLER_DEPLOY_RE = re.compile(r"\bwrangler\b.*\bdeploy\b|\bwrangler\s+pages\s+deploy\b", re.IGNORECASE)
WRANGLER_RE = re.compile(r"\bwrangler\b", re.IGNORECASE)
CANONICAL_GITHUB_PAGES_RE = re.compile(
    r"(?:canonical\s+production|production\s+target)[^\n.]*GitHub\s+Pages|"
    r"GitHub\s+Pages[^\n.]*canonical\s+production",
    re.IGNORECASE,
)
WRANGLER_OR_DOCKER_CANONICAL_RE = re.compile(
    r"(?:canonical\s+production|production\s+target)[^\n.]*\b(?:Wrangler|Cloudflare|Docker|docker-compose)\b|"
    r"\b(?:Wrangler|Cloudflare|Docker|docker-compose)\b[^\n.]*canonical\s+production",
    re.IGNORECASE,
)
LEGACY_CONTEXT_RE = re.compile(r"\b(?:legacy|fallback|secondary|not\s+the\s+canonical)\b", re.IGNORECASE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"FAIL: required file missing: {path.relative_to(ROOT)}")


def load_scripts() -> dict[str, str]:
    try:
        data = json.loads(read_text(PACKAGE_JSON))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: package.json is not valid JSON: {exc}")
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        raise SystemExit("FAIL: package.json has no scripts object")
    return {str(name): str(command) for name, command in scripts.items()}


def check_package_scripts(scripts: dict[str, str]) -> list[str]:
    failures: list[str] = []

    deploy = scripts.get("deploy")
    if not deploy:
        failures.append("package.json scripts.deploy is missing")
    else:
        if WRANGLER_RE.search(deploy):
            failures.append("package.json scripts.deploy must not invoke Wrangler")
        if WRANGLER_DEPLOY_RE.search(deploy):
            failures.append("package.json scripts.deploy invokes Wrangler deploy directly")
        if "GitHub Pages" not in deploy or "approval" not in deploy.lower():
            failures.append(
                "package.json scripts.deploy must fail fast and print that GitHub Pages is canonical and deploy approval is required"
            )
        if "process.exit(1)" not in deploy and "exit 1" not in deploy:
            failures.append("package.json scripts.deploy must exit non-zero")

    if "cf:deploy" in scripts:
        failures.append("package.json must not expose direct cf:deploy; use legacy:cf:deploy")

    if scripts.get("verify:deploy-posture") != "python3 scripts/verify_deploy_posture.py":
        failures.append("package.json scripts.verify:deploy-posture must run python3 scripts/verify_deploy_posture.py")

    verify = scripts.get("verify", "")
    if "verify:deploy-posture" not in verify:
        failures.append("package.json scripts.verify must include verify:deploy-posture")

    legacy_deploy = scripts.get("legacy:cf:deploy")
    if not legacy_deploy or not WRANGLER_DEPLOY_RE.search(legacy_deploy):
        failures.append("package.json must retain Wrangler deploy fallback as legacy:cf:deploy")

    for name, command in sorted(scripts.items()):
        if name == "deploy":
            continue
        if WRANGLER_RE.search(command) and not name.startswith("legacy:"):
            failures.append(f"package.json script {name!r} invokes Wrangler without a legacy: prefix")

    return failures


def check_canonical_docs(label: str, text: str) -> list[str]:
    failures: list[str] = []
    if not CANONICAL_GITHUB_PAGES_RE.search(text):
        failures.append(f"{label} must name GitHub Pages as canonical production")

    for match in WRANGLER_OR_DOCKER_CANONICAL_RE.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end].strip()
        if not LEGACY_CONTEXT_RE.search(line):
            failures.append(f"{label} presents Wrangler/Docker as canonical production: {line}")

    return failures


def check_runbook_secret_policy(text: str) -> list[str]:
    failures: list[str] = []
    required_fragments = [
        "Do not commit `.env`",
        "live secret values",
        "EVOMTRS_FORM_ENDPOINT",
        "Raw `EVOMTRS_FORM_ENDPOINT` values are never printed",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            failures.append(f"docs/github-pages-runbook.md must retain secret/.env guardrail: {fragment}")
    return failures


def check_workflow_launch_value_gate(text: str) -> list[str]:
    failures: list[str] = []
    required = {
        "manual workflow dispatch": "workflow_dispatch:",
        "static verification": "python3 scripts/verify_static.py dist",
        "launch-value verification": "python3 scripts/verify_launch_values.py dist",
        "Pages configuration": "actions/configure-pages@v5",
        "Pages artifact upload": "actions/upload-pages-artifact@v3",
        "endpoint GitHub secret": "EVOMTRS_FORM_ENDPOINT: ${{ secrets.EVOMTRS_FORM_ENDPOINT }}",
    }
    positions: dict[str, int] = {}
    for label, needle in required.items():
        position = text.find(needle)
        positions[label] = position
        if position == -1:
            failures.append(f"deploy workflow missing {label}: {needle}")

    if re.search(r"^\s*(?:push|pull_request):", text, re.MULTILINE):
        failures.append("deploy workflow must remain manual workflow_dispatch only")

    if not failures:
        if not (
            positions["static verification"]
            < positions["launch-value verification"]
            < positions["Pages configuration"]
            < positions["Pages artifact upload"]
        ):
            failures.append(
                "deploy workflow must run static verification, then launch-value verification, before Pages configure/upload"
            )
    return failures


def main() -> int:
    failures: list[str] = []
    scripts = load_scripts()
    readme = read_text(README)
    runbook = read_text(RUNBOOK)
    workflow = read_text(WORKFLOW)

    failures.extend(check_package_scripts(scripts))
    failures.extend(check_canonical_docs("README.md", readme))
    failures.extend(check_canonical_docs("docs/github-pages-runbook.md", runbook))
    failures.extend(check_runbook_secret_policy(runbook))
    failures.extend(check_workflow_launch_value_gate(workflow))

    if failures:
        print("Deploy posture verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Verified deploy posture guardrails:")
    print("- GitHub Pages remains canonical production in README/runbook")
    print("- generic npm run deploy fails fast without Wrangler")
    print("- Wrangler deploy fallback is legacy-prefixed")
    print("- runbook retains .env/live secret commit guardrails")
    print("- GitHub Pages workflow launch-value verification gates artifact upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
