# GitHub Pages Subpath Render Verification Fix Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Render EVOMTRS internal links and local assets so the site works both at a root domain like `https://evomtrs.com/` and at the GitHub Pages project URL `https://delicioushouse.github.io/evomtrs-site/`.

**Architecture:** Keep canonical SEO URLs absolute from `EVOMTRS_SITE_URL`, but render browser-facing same-site links/assets from a derived public base path. Extend the stdlib render/verify scripts so local verification simulates GitHub Pages project-subpath resolution and fails on root-relative links that would escape `/evomtrs-site/`.

**Tech Stack:** Static HTML templates in `public/**/*.html`, Python stdlib render and verification scripts, npm wrapper scripts, GitHub Pages static output in `dist/`.

---

## Context

Source Kanban task: `t_24397a52`
Source discovery task: `t_2da5dd0a`
Board: `evomtrs-site`
Workspace: `/home/node/evomtrs-site`
Date: 2026-07-03

Verified current state from repo inspection:

- `scripts/render_site.py:42-119` requires `EVOMTRS_SITE_URL` and renders only existing `EVOMTRS_*` template tokens.
- `scripts/render_site.py:122-142` performs direct text replacement, so adding a new token is low-risk and does not require a templating dependency.
- `scripts/verify_static.py:153-191` validates root-relative links against the local `dist/` filesystem, which passes even though GitHub Pages resolves `/assets/...` at `https://delicioushouse.github.io/assets/...`.
- `scripts/verify_static.py:115-150` already treats sitemap and robots as absolute URL contracts tied to `EVOMTRS_SITE_URL`.
- `public/**/*.html` hard-codes browser-facing same-site URLs such as `/assets/css/styles.min.css`, `/assets/js/main.js`, `/favicon.svg`, `/services/`, `/contact/`, and `/#faq`.
- `.env.example:4` currently sets `EVOMTRS_SITE_URL=https://evomtrs.com`, which exercises only the root-domain case.
- `docs/github-pages-runbook.md:50-78` documents local preflight, but not project-subpath verification.

Live issue this plan fixes:

- At `https://delicioushouse.github.io/evomtrs-site/`, root-relative links like `/assets/css/styles.min.css` escape the project path and request `https://delicioushouse.github.io/assets/css/styles.min.css`, producing 404s.
- Navigation links like `/services/` similarly escape to `https://delicioushouse.github.io/services/` instead of `https://delicioushouse.github.io/evomtrs-site/services/`.

## Hard gates and non-goals

Do not perform any of these during implementation:

- Do not deploy, run `gh workflow run`, push, merge, dispatch workflows, mutate GitHub Pages settings, mutate variables/secrets, change DNS/custom domains, switch production traffic, or disable/unpublish Pages.
- Do not change owner launch values or expose raw `EVOMTRS_FORM_ENDPOINT` values.
- Do not change visual styling, content hierarchy, premium motion, or nav labels. This fix changes link targets only.
- Do not replace the static renderer with a new framework or templating engine.
- Do not make `dist/` a committed artifact.

Allowed scope:

- Edit checked-in templates/scripts/docs.
- Run local builds and verification against `.env.example` and temporary test env files.
- Add verification modes that simulate GitHub Pages project-subpath behavior.

## Base-path decision

Use a derived base path from `EVOMTRS_SITE_URL`, with an optional explicit override for future safety.

Implementation contract:

1. Parse `EVOMTRS_SITE_URL` with `urllib.parse.urlparse`.
2. Normalize the parsed path into `EVOMTRS_BASE_PATH`:
   - `https://evomtrs.com` -> empty string `""`
   - `https://evomtrs.com/` -> empty string `""`
   - `https://delicioushouse.github.io/evomtrs-site/` -> `"/evomtrs-site"`
   - `https://example.com/sub/site/` -> `"/sub/site"`
3. Allow optional `EVOMTRS_PUBLIC_BASE_PATH` to override the derived path when set. This is public-safe, not a secret.
4. Normalize `EVOMTRS_PUBLIC_BASE_PATH` the same way:
   - empty or `/` -> empty string `""`
   - `evomtrs-site` -> `"/evomtrs-site"`
   - `/evomtrs-site/` -> `"/evomtrs-site"`
5. Reject invalid base paths early in `scripts/render_site.py`:
   - absolute URLs
   - query strings or fragments
   - `..` path traversal segments
   - duplicate slashes after normalization, except the leading slash
6. Render browser-facing local links/assets with `__EVOMTRS_BASE_PATH__`.
7. Keep canonical, OpenGraph URL, JSON-LD `url`, sitemap, and robots sitemap absolute from `EVOMTRS_SITE_URL`.

Why this is the right cut:

- The production Pages URL already contains the project path, so deriving from `EVOMTRS_SITE_URL` is enough for the current failure.
- A future custom domain naturally derives an empty base path, so `https://evomtrs.com/` remains clean.
- The optional override prevents a future hosting edge case from requiring a renderer rewrite.
- The variable is public-safe, so it can be a repo/environment variable if needed without touching secrets.

## URL rendering rules

Use these exact patterns in templates:

```html
<link rel="canonical" href="__EVOMTRS_SITE_URL__/services/" />
<meta property="og:url" content="__EVOMTRS_SITE_URL__/services/" />
<meta property="og:image" content="__EVOMTRS_SITE_URL__/assets/images/example.webp" />
<link rel="stylesheet" href="__EVOMTRS_BASE_PATH__/assets/css/styles.min.css" />
<a href="__EVOMTRS_BASE_PATH__/services/">Services</a>
<a href="__EVOMTRS_BASE_PATH__/#faq">FAQ</a>
<script defer src="__EVOMTRS_BASE_PATH__/assets/js/main.js"></script>
```

Expected output examples:

```text
EVOMTRS_SITE_URL=https://evomtrs.com
__EVOMTRS_BASE_PATH__/assets/css/styles.min.css -> /assets/css/styles.min.css
__EVOMTRS_BASE_PATH__/services/ -> /services/
__EVOMTRS_BASE_PATH__/#faq -> /#faq
canonical services URL -> https://evomtrs.com/services/
robots sitemap -> Sitemap: https://evomtrs.com/sitemap.xml
```

```text
EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/
__EVOMTRS_BASE_PATH__/assets/css/styles.min.css -> /evomtrs-site/assets/css/styles.min.css
__EVOMTRS_BASE_PATH__/services/ -> /evomtrs-site/services/
__EVOMTRS_BASE_PATH__/#faq -> /evomtrs-site/#faq
canonical services URL -> https://delicioushouse.github.io/evomtrs-site/services/
robots sitemap -> Sitemap: https://delicioushouse.github.io/evomtrs-site/sitemap.xml
```

## Files likely touched

- Modify: `scripts/render_site.py`
- Modify: `scripts/verify_static.py`
- Modify: `public/index.html`
- Modify: `public/services/index.html`
- Modify: `public/gallery/index.html`
- Modify: `public/about/index.html`
- Modify: `public/testimonials/index.html`
- Modify: `public/contact/index.html`
- Modify: `public/privacy-policy/index.html`
- Modify: `public/terms-of-use/index.html`
- Modify: `.env.example` only if the implementer chooses to document `EVOMTRS_PUBLIC_BASE_PATH=` explicitly. Prefer not making it required.
- Modify: `docs/github-pages-runbook.md`
- Modify: `package.json` only if adding a named convenience script for project-subpath verification.
- Do not edit generated `dist/` as source.

## P0 vertical slice cutline

Smallest safe implementation:

1. Add `EVOMTRS_BASE_PATH` render support.
2. Replace every browser-facing same-site root-relative URL in `public/**/*.html` with `__EVOMTRS_BASE_PATH__...`.
3. Extend `scripts/verify_static.py` to fail when same-site links/assets are not scoped under the derived base path for project-subpath URLs.
4. Add a no-commit temporary env verification command for `https://delicioushouse.github.io/evomtrs-site/`.
5. Update runbook docs with the new local verification command and later no-mutation live smoke plan.

Defer:

- Large template partial extraction for shared nav/footer. That is a good cleanup later, but not necessary to fix the production break.
- Automated live browser QA. This task is no-deploy/no-mutation planning. Live smoke belongs after approved deployment.

---

## Task 1: Add base-path derivation tests as a temporary executable check

**Objective:** Lock the URL contract before implementation changes behavior.

**Files:**

- Inspect: `scripts/render_site.py:42-119`
- Modify later: `scripts/render_site.py`

**Step 1: Write a temporary failing probe command**

Run before implementation:

```bash
python3 - <<'PY'
from urllib.parse import urlparse

def expected(site_url, override=None):
    # This is the contract implementation will move into scripts/render_site.py.
    raw = override if override is not None and override.strip() else urlparse(site_url).path
    raw = raw.strip()
    if raw in ('', '/'):
        return ''
    if '://' in raw or '?' in raw or '#' in raw:
        raise ValueError(raw)
    parts = [part for part in raw.split('/') if part]
    if any(part == '..' for part in parts):
        raise ValueError(raw)
    return '/' + '/'.join(parts)

cases = [
    ('https://evomtrs.com', None, ''),
    ('https://evomtrs.com/', None, ''),
    ('https://delicioushouse.github.io/evomtrs-site/', None, '/evomtrs-site'),
    ('https://example.com/sub/site/', None, '/sub/site'),
    ('https://evomtrs.com', 'evomtrs-site', '/evomtrs-site'),
    ('https://evomtrs.com', '/evomtrs-site/', '/evomtrs-site'),
]
for site_url, override, want in cases:
    got = expected(site_url, override)
    assert got == want, (site_url, override, got, want)
print('base-path contract examples pass')
PY
```

Expected now: PASS for the probe, but no production code exposes this behavior yet.

**Step 2: Implement the real helper in the next task**

Do not keep the temporary probe as a committed test file unless the repo adds a test harness. The permanent coverage comes from `verify_static.py` and local render commands.

## Task 2: Add `EVOMTRS_BASE_PATH` support in the renderer

**Objective:** Make the renderer expose a normalized base-path token derived from `EVOMTRS_SITE_URL` or optional `EVOMTRS_PUBLIC_BASE_PATH`.

**Files:**

- Modify: `scripts/render_site.py:4-119`

**Step 1: Add stdlib import**

Add:

```python
from urllib.parse import urlparse
```

**Step 2: Add helper near `is_placeholder_phone`**

Add:

```python
def normalize_public_base_path(site_url: str, override: str | None = None) -> str:
    raw_path = (override or "").strip()
    if not raw_path:
        raw_path = urlparse(site_url).path
    raw_path = raw_path.strip()
    if raw_path in {"", "/"}:
        return ""
    if "://" in raw_path or "?" in raw_path or "#" in raw_path:
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH: {raw_path!r}")
    parts = [part for part in raw_path.split("/") if part]
    if any(part == ".." for part in parts):
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH traversal segment: {raw_path!r}")
    return "/" + "/".join(parts)
```

**Step 3: Compute the token in `required_env()`**

After `site_url = os.environ["EVOMTRS_SITE_URL"].rstrip("/")`, add:

```python
base_path = normalize_public_base_path(
    site_url,
    os.environ.get("EVOMTRS_PUBLIC_BASE_PATH"),
)
```

After `values["EVOMTRS_SITE_URL"] = site_url`, add:

```python
values["EVOMTRS_BASE_PATH"] = base_path
```

Do not add `EVOMTRS_PUBLIC_BASE_PATH` to the required `keys` list. It is optional.

**Step 4: Verify syntax**

Run:

```bash
python3 -m py_compile scripts/render_site.py
```

Expected: exits 0.

## Task 3: Convert browser-facing same-site template URLs

**Objective:** Keep visual behavior the same while scoping all local browser requests under the project base path when needed.

**Files:**

- Modify: `public/index.html`
- Modify: `public/services/index.html`
- Modify: `public/gallery/index.html`
- Modify: `public/about/index.html`
- Modify: `public/testimonials/index.html`
- Modify: `public/contact/index.html`
- Modify: `public/privacy-policy/index.html`
- Modify: `public/terms-of-use/index.html`

**Step 1: Replace local asset references**

Replace these patterns across `public/**/*.html`:

```text
href="/favicon.svg" -> href="__EVOMTRS_BASE_PATH__/favicon.svg"
href="/favicon.ico" -> href="__EVOMTRS_BASE_PATH__/favicon.ico"
href="/assets/ -> href="__EVOMTRS_BASE_PATH__/assets/
src="/assets/ -> src="__EVOMTRS_BASE_PATH__/assets/
srcset="/assets/ -> srcset="__EVOMTRS_BASE_PATH__/assets/
, /assets/ -> , __EVOMTRS_BASE_PATH__/assets/
src="/assets/js/main.js" -> src="__EVOMTRS_BASE_PATH__/assets/js/main.js"
```

**Step 2: Replace route links**

Replace same-site route links:

```text
href="/" -> href="__EVOMTRS_BASE_PATH__/"
href="/services/" -> href="__EVOMTRS_BASE_PATH__/services/"
href="/gallery/" -> href="__EVOMTRS_BASE_PATH__/gallery/"
href="/about/" -> href="__EVOMTRS_BASE_PATH__/about/"
href="/testimonials/" -> href="__EVOMTRS_BASE_PATH__/testimonials/"
href="/contact/" -> href="__EVOMTRS_BASE_PATH__/contact/"
href="/privacy-policy/" -> href="__EVOMTRS_BASE_PATH__/privacy-policy/"
href="/terms-of-use/" -> href="__EVOMTRS_BASE_PATH__/terms-of-use/"
href="/#faq" -> href="__EVOMTRS_BASE_PATH__/#faq"
```

Do not replace:

- `href="#main"`, because that is an in-page skip link.
- `tel:`, `sms:`, `mailto:`, `https://...`, or owner-provided map/form URLs.
- `__EVOMTRS_SITE_URL__` absolute SEO/social/schema values.
- `robots.txt` and `sitemap.xml` template values.

**Step 3: Search for missed root-relative same-site URLs**

Run:

```bash
grep -RInE 'href="/|src="/|srcset="/|, /assets/|action="/' public --include='*.html'
```

Expected after implementation: no matches except any intentionally reviewed in-page or external-safe case. If any remain, inspect and either convert or document why safe.

## Task 4: Extend static verification for project-subpath resolution

**Objective:** Make `npm run verify` fail on the exact bug live users saw under `/evomtrs-site/`.

**Files:**

- Modify: `scripts/verify_static.py:10-191`

**Step 1: Import needed parser support**

`urlparse` already exists. Add helper functions below `route_file()` or near link helpers.

**Step 2: Add base-path normalization helper matching renderer behavior**

Add:

```python
def normalize_public_base_path(site_url: str, override: str | None = None) -> str:
    raw_path = (override or "").strip()
    if not raw_path:
        raw_path = urlparse(site_url).path
    raw_path = raw_path.strip()
    if raw_path in {"", "/"}:
        return ""
    if "://" in raw_path or "?" in raw_path or "#" in raw_path:
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH: {raw_path!r}")
    parts = [part for part in raw_path.split("/") if part]
    if any(part == ".." for part in parts):
        raise SystemExit(f"Invalid EVOMTRS_PUBLIC_BASE_PATH traversal segment: {raw_path!r}")
    return "/" + "/".join(parts)
```

If duplication bothers the implementer, keep it duplicated for this slice. A shared module is unnecessary until a second or third renderer/verifier needs the same helper.

**Step 3: Add browser-to-local path conversion**

Add:

```python
def strip_base_path_for_local_target(url_path: str, base_path: str) -> str | None:
    if not base_path:
        return url_path or "/"
    if url_path == base_path:
        return "/"
    prefix = f"{base_path}/"
    if url_path.startswith(prefix):
        return "/" + url_path[len(prefix):]
    return None
```

**Step 4: Update local target checking**

Change `local_link_target_exists(dist_dir: Path, url: str) -> bool` to accept `base_path: str` and resolve only after stripping the base path:

```python
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
```

**Step 5: Update core link expectations**

For each HTML page, expected core links should include the base path:

```python
def browser_path(route: str, base_path: str) -> str:
    if not base_path:
        return route
    if route == "/":
        return f"{base_path}/"
    return f"{base_path}{route}"
```

Then in `check_links`, compare `page_hrefs` against `[browser_path(route, base_path) for route in CORE_LINKS]`.

**Step 6: Make root-relative escape failures explicit**

When `base_path` is non-empty and a local URL starts with `/` but not with the base path, report:

```text
index.html references root-relative href /services/ outside configured base path /evomtrs-site
```

This is the regression that would have caught the live GitHub Pages break.

**Step 7: Wire env value into main**

After loading `site_url`, compute:

```python
base_path = normalize_public_base_path(
    site_url,
    env_values.get("EVOMTRS_PUBLIC_BASE_PATH"),
)
```

Call:

```python
failures.extend(check_links(dist_dir, base_path))
```

Print the base path in success output:

```python
print(f"public base path: {base_path or '/'}")
```

**Step 8: Verify syntax**

Run:

```bash
python3 -m py_compile scripts/verify_static.py
```

Expected: exits 0.

## Task 5: Add project-subpath regression verification command

**Objective:** Prove the verifier catches the Pages project-path case without touching GitHub.

**Files:**

- Modify: `package.json:6-14` only if choosing a named script
- Modify: `docs/github-pages-runbook.md:50-78`

**Step 1: Create a temporary env file in `/tmp`**

Run after Tasks 2-4 are implemented:

```bash
python3 - <<'PY'
from pathlib import Path
src = Path('.env.example').read_text(encoding='utf-8')
out = src.replace('EVOMTRS_SITE_URL=https://evomtrs.com', 'EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/')
Path('/tmp/evomtrs-pages-subpath.env').write_text(out, encoding='utf-8')
PY
```

**Step 2: Render and verify the project-subpath case**

Run:

```bash
python3 scripts/render_site.py public /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
python3 scripts/verify_static.py /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
```

Expected after implementation:

```text
Rendered public -> /tmp/evomtrs-pages-subpath-dist
Verified rendered static site: /tmp/evomtrs-pages-subpath-dist
Required routes: 8
sitemap.xml: ok
robots.txt: ok
local links/assets: ok
public base path: /evomtrs-site
unreplaced template tokens: none
```

**Step 3: Prove the old bug would fail**

Before converting all templates, or with a controlled temporary mutation, the verifier should emit failures like:

```text
Static verification failed:
- index.html references root-relative href target /services/ outside configured base path /evomtrs-site
- index.html references root-relative src target /assets/images/... outside configured base path /evomtrs-site
```

Do not commit a negative fixture unless the implementer adds a proper test harness. The important requirement is that `verify_static.py` is path-aware and fails naturally if someone reintroduces root-relative same-site links in a project-subpath render.

**Step 4: Optional package script**

If the team wants this check as a stable command, add:

```json
"verify:pages-subpath-local": "python3 - <<'PY'\nfrom pathlib import Path\nsrc = Path('.env.example').read_text(encoding='utf-8')\nout = src.replace('EVOMTRS_SITE_URL=https://evomtrs.com', 'EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/')\nPath('/tmp/evomtrs-pages-subpath.env').write_text(out, encoding='utf-8')\nPY\npython3 scripts/render_site.py public /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env && python3 scripts/verify_static.py /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env"
```

Prefer keeping this as documented commands unless package-script escaping becomes readable enough. Python one-liners inside JSON are easy to turn into soup.

## Task 6: Validate root-domain behavior still works

**Objective:** Ensure the current custom/root-domain path remains unchanged.

**Files:**

- Verify only: `dist/`, generated by `npm run build:example`

**Step 1: Run root-domain local verification**

Run:

```bash
npm run --silent verify
npm run --silent verify:launch-local
```

Expected:

- Both exit 0.
- `verify_static.py` reports `public base path: /`.
- Existing sitemap/robots checks still pass against `https://evomtrs.com`.
- Launch-value placeholder checks remain unchanged.

**Step 2: Inspect generated root-domain URLs**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
home = Path('dist/index.html').read_text(encoding='utf-8')
checks = [
    'href="/assets/css/styles.min.css"',
    'src="/assets/js/main.js"',
    'href="/services/"',
    'href="/#faq"',
    'href="https://evomtrs.com/"',
]
for check in checks:
    print(check, 'OK' if check in home else 'MISSING')
PY
```

Expected: all `OK` for root-domain `.env.example` render.

## Task 7: Validate project-subpath generated URLs

**Objective:** Ensure generated Pages output requests local assets/routes under `/evomtrs-site/` while SEO URLs remain absolute.

**Files:**

- Verify only: `/tmp/evomtrs-pages-subpath-dist`

**Step 1: Render the project-subpath environment**

Run:

```bash
python3 scripts/render_site.py public /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
```

Expected: exits 0.

**Step 2: Assert rendered browser-facing URLs**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
home = Path('/tmp/evomtrs-pages-subpath-dist/index.html').read_text(encoding='utf-8')
checks = [
    'href="/evomtrs-site/assets/css/styles.min.css"',
    'src="/evomtrs-site/assets/js/main.js"',
    'href="/evomtrs-site/services/"',
    'href="/evomtrs-site/#faq"',
    'href="https://delicioushouse.github.io/evomtrs-site/"',
    'content="https://delicioushouse.github.io/evomtrs-site/assets/images/',
]
for check in checks:
    print(check, 'OK' if check in home else 'MISSING')
PY
```

Expected: all `OK`.

**Step 3: Assert no escaping root-relative same-site URLs remain**

Run:

```bash
python3 - <<'PY'
import html.parser
from pathlib import Path
from urllib.parse import urlparse

BASE = '/evomtrs-site'
BAD = []
ATTRS = {'href', 'src', 'action'}

class P(html.parser.HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if not value:
                continue
            values = []
            if name in ATTRS:
                values = [value]
            elif name == 'srcset':
                values = [part.strip().split()[0] for part in value.split(',') if part.strip()]
            for url in values:
                parsed = urlparse(url)
                if parsed.scheme or parsed.netloc or url.startswith('#'):
                    continue
                path = parsed.path
                if path.startswith('/') and not (path == BASE or path.startswith(BASE + '/')):
                    BAD.append((self.path, name, url))

for file in Path('/tmp/evomtrs-pages-subpath-dist').rglob('*.html'):
    parser = P(file)
    parser.feed(file.read_text(encoding='utf-8'))
if BAD:
    for item in BAD:
        print('BAD', item)
    raise SystemExit(1)
print('subpath root-relative escape check: ok')
PY
```

Expected: exits 0 and prints `subpath root-relative escape check: ok`.

## Task 8: Update runbook documentation

**Objective:** Make future operators run the exact local checks that catch this class of GitHub Pages breakage.

**Files:**

- Modify: `docs/github-pages-runbook.md:50-78`

**Step 1: Add a local project-subpath preflight section**

Add after local non-live preflight. Use a four-backtick outer fence if copying this section through Markdown tooling, because the section contains its own shell fence:

````markdown
## GitHub Pages project-subpath preflight

For the public project URL `https://delicioushouse.github.io/evomtrs-site/`, local assets and nav links must render under `/evomtrs-site/`. Root-relative `/assets/...` and `/services/` links are broken on GitHub Pages project sites because they escape to `https://delicioushouse.github.io/...`.

Run without mutating GitHub:

```bash
python3 - <<'PY'
from pathlib import Path
src = Path('.env.example').read_text(encoding='utf-8')
out = src.replace('EVOMTRS_SITE_URL=https://evomtrs.com', 'EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/')
Path('/tmp/evomtrs-pages-subpath.env').write_text(out, encoding='utf-8')
PY
python3 scripts/render_site.py public /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
python3 scripts/verify_static.py /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
```

Expected: `verify_static.py` reports `public base path: /evomtrs-site` and exits 0.
````

**Step 2: Add no-mutation live smoke commands for later approved deployment**

Add to post-deploy smoke:

```bash
SITE="https://delicioushouse.github.io/evomtrs-site"
for path in / /services/ /gallery/ /about/ /testimonials/ /contact/ /privacy-policy/ /terms-of-use/ /assets/css/styles.min.css /assets/js/main.js /favicon.svg; do
  curl -fsSI "$SITE$path" | sed -n "1,5p"
done
curl -fsS "$SITE/" -o /tmp/evomtrs-pages-home.html
python3 - <<'PY'
from pathlib import Path
html = Path('/tmp/evomtrs-pages-home.html').read_text(encoding='utf-8')
required = [
    'href="/evomtrs-site/assets/css/styles.min.css"',
    'src="/evomtrs-site/assets/js/main.js"',
    'href="/evomtrs-site/services/"',
    'href="/evomtrs-site/contact/"',
]
missing = [needle for needle in required if needle not in html]
if missing:
    raise SystemExit('Missing subpath-scoped URLs: ' + ', '.join(missing))
print('live subpath-scoped URL smoke: ok')
PY
```

Mark this as post-deploy/no-mutation. It reads public URLs only and does not authorize deployment.

## Task 9: Full local verification before review

**Objective:** Prove the code change works locally and did not regress existing launch checks.

**Files:**

- Verify only

**Step 1: Run required checks**

Run:

```bash
npm run build
npm run --silent verify
npm run --silent verify:launch-local
python3 -m py_compile scripts/render_site.py scripts/verify_static.py scripts/verify_launch_values.py scripts/verify_deploy_posture.py
git diff --check
```

Expected:

- All commands exit 0.
- `npm run build` renders `dist/` from the current environment or fails clearly if required live env vars are absent. If local live env vars are absent, run `npm run build:example` and record that `npm run build` requires configured `EVOMTRS_*` env values.
- `npm run --silent verify` exits 0.
- `npm run --silent verify:launch-local` exits 0.
- `py_compile` exits 0.
- `git diff --check` exits 0.

**Step 2: Run project-subpath verification**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
src = Path('.env.example').read_text(encoding='utf-8')
out = src.replace('EVOMTRS_SITE_URL=https://evomtrs.com', 'EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/')
Path('/tmp/evomtrs-pages-subpath.env').write_text(out, encoding='utf-8')
PY
python3 scripts/render_site.py public /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
python3 scripts/verify_static.py /tmp/evomtrs-pages-subpath-dist --env-file /tmp/evomtrs-pages-subpath.env
```

Expected: exits 0 and reports `public base path: /evomtrs-site`.

## Task 10: Review gates before implementation is ship-ready

**Objective:** Keep this from being treated as production-ready just because local checks pass.

**Files:**

- Review artifact: Kanban comment or PR review output

Required review gates after implementation:

1. Eng review (`plan-eng-review` or equivalent reviewer pass on final diff): confirm URL contract, canonical/sitemap/robots separation, custom-domain behavior, and path validation.
2. DevEx review (`plan-devex-review` or equivalent reviewer pass): confirm local verification commands are discoverable, failure messages name the actual broken URL class, and operators do not need GitHub mutation to reproduce the issue.
3. Design review (`plan-design-review` or equivalent visual/nav behavior pass): required because nav/link behavior changes what users can click, even though labels and styling should not change.
4. Code review (`review`): required before merge/ship-ready status.
5. QA after approved deployment: public no-mutation smoke of routes, assets, favicon, sitemap, robots, and rendered subpath-scoped URLs.

This plan itself does not authorize deployment or production traffic changes.

## Suggested implementation handoff card

Create a separate implementation task after this plan is accepted:

Title: `Implement EVOMTRS GitHub Pages subpath render and verification fix`

Assignee: `dept-eng` or the project implementation profile already used for EVOMTRS code work.

Body:

```text
Implement docs/plans/2026-07-03-github-pages-subpath-render-verification-fix.md.
Do not deploy, dispatch workflows, mutate GitHub settings/variables/secrets, push/merge, or change production traffic.
Acceptance: all Task 9 checks pass, project-subpath verification catches/guards against root-relative link escapes, and required review gates are posted before ship-ready.
```

## GSTACK REVIEW REPORT

| Review | Verdict | Findings | Plan changes made |
| --- | --- | ---: | --- |
| Eng review | PASS WITH GUARDS | 3 | Added explicit canonical/sitemap/robots separation, optional override validation, and custom-domain examples. |
| DevEx review | PASS WITH GUARDS | 2 | Added temporary env reproduction commands, expected failure text, and runbook update requirements. |
| Design review | PASS WITH GUARDS | 1 | Required nav labels/styling to remain unchanged and added post-change design/nav behavior review gate. |
| Code review | NOT RUN ON CODE | 0 | Implementation diff must run `/review` or equivalent before merge. |
| QA | DEFERRED | 0 | Live smoke is no-mutation and only allowed after approved deployment. |

## Final acceptance checklist

- [ ] `scripts/render_site.py` derives and renders `EVOMTRS_BASE_PATH`.
- [ ] All browser-facing same-site template links/assets use `__EVOMTRS_BASE_PATH__`.
- [ ] Canonical, OG URL, JSON-LD URL/image, sitemap, and robots remain absolute from `EVOMTRS_SITE_URL`.
- [ ] `scripts/verify_static.py` fails for root-relative same-site links that escape a non-empty project base path.
- [ ] Root-domain verification passes with `.env.example`.
- [ ] Project-subpath verification passes with `EVOMTRS_SITE_URL=https://delicioushouse.github.io/evomtrs-site/`.
- [ ] `npm run build` or documented equivalent, `npm run --silent verify`, `npm run --silent verify:launch-local`, `py_compile`, and `git diff --check` pass.
- [ ] Runbook documents local project-subpath preflight and later no-mutation live smoke.
- [ ] Required review gates are complete before implementation is marked ship-ready.

## Implementation readiness

Ready for a separate implementation task: yes.

Ship-ready now: no. This is a plan only. Code implementation, local verification, review, and approved deployment/QA remain separate work.
