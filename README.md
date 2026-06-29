# EVOMTRS Static Website

Static marketing site targeting `https://evomtrs.com`; production dispatch remains gated by owner-approved values, GitHub Pages setup, and the launch runbook.

Canonical production deployment target: GitHub Pages via the manual `.github/workflows/deploy-github-pages.yml` workflow. See `docs/github-pages-runbook.md` for the deployment gate, required GitHub variables/secrets, smoke checks, and rollback steps.

Current launch-gate sources, in order:

1. `docs/launch-owner-questions.md` for owner approvals.
2. `docs/launch-values-approval-checklist.md` for public values, secret handling, legal/proof gates.
3. `docs/github-pages-runbook.md` for operator setup, smoke, and rollback.
4. Historical reports (`FINAL_REPORT.md`, `REDESIGN.md`) are audit/design artifacts, not current launch gates.

## Deployment posture

Primary production path:

- Build `dist/` with `npm run build`.
- Verify the static output with `npm run verify` before packaging deployment changes.
- Deploy through the manual GitHub Pages workflow after repository variables/secrets and owner approval are in place.

Legacy/secondary tooling:

- Cloudflare/Wrangler scripts and `wrangler.jsonc` remain available for local Cloudflare-style preview or a future fallback target, but they are not the canonical production deployment path.
- `docker-compose.yml` remains a legacy container runtime for an Nginx Proxy Manager/shared Docker network setup; do not treat it as the active production target unless the owner explicitly re-selects Docker hosting.
- Do not dispatch deploy workflows, mutate secrets/variables, or switch production traffic as part of routine documentation or local build work.

## Structure

- `public/` HTML templates and static assets
- `scripts/convert-images.sh` approved EVOMTRS image conversion pipeline
- `scripts/render_site.py` env-driven site renderer
- `scripts/render-site.sh` local render wrapper
- `.github/workflows/deploy-github-pages.yml` manual GitHub Pages deployment workflow
- `docs/github-pages-runbook.md` deployment runbook and production release gate
- `docker-compose.yml` legacy Docker runtime on `shared_webnet`

## Environment

Copy `.env.example` to `.env` only for local preview/example rendering. The complete production variable/secret list lives in `docs/github-pages-runbook.md`; do not infer missing production values from `.env.example`, and do not treat it as owner-approved launch data.

For production, set public values as GitHub repository/environment variables and set `EVOMTRS_FORM_ENDPOINT` as a GitHub secret unless the owner confirms it is public-safe. Keep raw endpoint values out of docs, Kanban comments, and PR bodies.

## Local Render

```bash
./scripts/convert-images.sh
./scripts/render-site.sh
python3 -m http.server 8080 --directory dist
```

## npm Build Workflow

The site can also be built and served using npm:

```bash
npm install
npm run build
npm run serve
```

Useful scripts:

- `npm run build` renders `public/` templates into `dist/`
- `npm run build:example` renders with `.env.example` in a clean environment
- `npm run verify` renders with `.env.example`, verifies static output, and checks GitHub Pages deploy-posture guardrails
- `npm run serve` renders and serves `dist/` locally on port `8080`
- `npm run legacy:cf:dev` renders and runs Cloudflare Pages local dev (`wrangler pages dev`) for legacy Cloudflare-style preview only
- `npm run deploy` fails fast because GitHub Pages is the canonical production target and deploy approval is required before running the manual workflow
- `npm run legacy:cf:deploy` and `npm run legacy:cf:preview` retain Wrangler fallback commands for explicitly approved legacy Cloudflare work only

## GitHub Pages Setup

Use `docs/github-pages-runbook.md` as the operator source of truth after owner approvals in `docs/launch-owner-questions.md` and `docs/launch-values-approval-checklist.md` are resolved. Historical reports (`FINAL_REPORT.md`, `REDESIGN.md`) are not launch gates. Summary:

- Pages source: GitHub Actions
- Workflow: `.github/workflows/deploy-github-pages.yml`
- Trigger policy: manual `workflow_dispatch` only until one manual deployment has passed build, smoke, and rollback review
- Build command: `npm run build`
- Build output directory: `dist`

Set production `EVOMTRS_*` values in GitHub variables/secrets as described in the runbook, not in committed files.

## Legacy Cloudflare/Wrangler Setup

Cloudflare Pages and Wrangler are retained as secondary/fallback tooling only. If the owner re-selects Cloudflare as the production target, use these project settings:

- Framework preset: `None`
- Build command: `npm run build`
- Build output directory: `dist`

Required build-time `EVOMTRS_*` values should match the GitHub Pages runbook. Do not run Wrangler deploy commands without an explicit deploy approval.

## Legacy Docker Runtime

```bash
docker compose up --build -d
```

The container serves rendered output on internal port `8080` and joins the external Docker network `shared_webnet` so Nginx Proxy Manager can forward traffic to it. This is legacy/fallback hosting guidance, not the current canonical production path while GitHub Pages is selected.
