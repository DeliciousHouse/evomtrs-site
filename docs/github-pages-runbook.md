# GitHub Pages deployment runbook

Production target: GitHub Pages.

This repository did not have a checked-in GitHub Actions workflow for Pages deployment when inspected on this runner. The proposed workflow is `.github/workflows/deploy-github-pages.yml`.

## Safety policy

- Do not commit `.env`, `.env.local`, `.env.*.local`, `.dev.vars*`, `.wrangler`, `dist/`, or live secret values.
- Keep production `EVOMTRS_*` values in GitHub repository/environment variables or secrets.
- Treat `EVOMTRS_FORM_ENDPOINT` as a secret unless the owner confirms it is public-safe.
- Use `workflow_dispatch` first. Do not enable push-triggered deploys until one manual deployment has passed build, smoke, and rollback review.

## Required GitHub Pages settings

In GitHub repository settings:

1. Pages source: GitHub Actions.
2. Environment: `github-pages`.
3. Branch protection/review gates: require review if this site is production-critical.

## Required GitHub variables

Set these as repository or `github-pages` environment variables:

- `EVOMTRS_SITE_URL`
- `EVOMTRS_BUSINESS_NAME`
- `EVOMTRS_CONTACT_EMAIL`
- `EVOMTRS_CONTACT_PHONE_E164`
- `EVOMTRS_CONTACT_PHONE_DISPLAY`
- `EVOMTRS_TEXT_PHONE_E164`
- `EVOMTRS_ADDRESS_LINE1`
- `EVOMTRS_CITY`
- `EVOMTRS_STATE`
- `EVOMTRS_ZIP`
- `EVOMTRS_PRICE_RANGE`
- `EVOMTRS_FOUNDER_NAME`
- `EVOMTRS_FOUNDER_ROLE`
- `EVOMTRS_FOUNDER_CREDENTIAL`
- `EVOMTRS_LEGAL_UPDATED_DATE`
- `EVOMTRS_DIRECTIONS_URL`
- `EVOMTRS_MAP_EMBED_URL`

Set this as a GitHub secret:

- `EVOMTRS_FORM_ENDPOINT`

## Local non-live preflight

From repo root:

```bash
git status --short --branch
git check-ignore -q .env.local
python3 scripts/render_site.py public /tmp/evomtrs-local-render --env-file .env.local
python3 scripts/verify_static.py /tmp/evomtrs-local-render --env-file .env.local
npm run --silent verify
```

Expected result:

- `.env.local` is ignored.
- Local render exits 0.
- Static verification exits 0.
- Required routes: 8.
- Sitemap, robots, local links/assets, and unreplaced token checks pass.

## Deploy preflight

Requires authenticated GitHub CLI or browser access with repo admin/settings rights:

```bash
gh auth status
gh repo view DeliciousHouse/evomtrs-site --json nameWithOwner,visibility,defaultBranchRef
```

Confirm before dispatch:

- Pages source is GitHub Actions.
- All variables/secrets above exist in the selected GitHub scope.
- The workflow file has been merged to the default branch.
- Production hostname is confirmed. The user stated production is on GitHub Pages; `EVOMTRS_SITE_URL` should match the public Pages/custom domain.

Manual dispatch after merge:

```bash
gh workflow run deploy-github-pages.yml --repo DeliciousHouse/evomtrs-site --ref main
```

## Post-deploy smoke

Replace `$SITE` with `EVOMTRS_SITE_URL`:

```bash
curl -fsSI "$SITE/" | sed -n '1,20p'
curl -fsS "$SITE/" -o /tmp/evomtrs-home.html
grep -q 'EVOMTRS' /tmp/evomtrs-home.html
! grep -R '__EVOMTRS_' /tmp/evomtrs-home.html
! grep -R '\[REPLACE_WITH_' /tmp/evomtrs-home.html
curl -fsS "$SITE/sitemap.xml" | sed -n '1,20p'
curl -fsS "$SITE/robots.txt"
```

Spot-check required routes:

```bash
for path in / /services/ /gallery/ /about/ /testimonials/ /contact/ /privacy-policy/ /terms-of-use/; do
  curl -fsSI "$SITE$path" | sed -n "1,5p"
done
```

## Rollback

Preferred rollback:

1. In GitHub Actions, re-run the last known-good `Deploy GitHub Pages` workflow run from the last known-good commit.
2. If the bad workflow file caused the issue, revert the workflow/content commit and dispatch again.
3. Re-run the post-deploy smoke checks.

Emergency rollback if GitHub Pages custom domain is broken:

- In repository Pages settings, remove or correct the custom domain/CNAME only with owner approval.
- Re-run smoke after DNS/TLS settles.
