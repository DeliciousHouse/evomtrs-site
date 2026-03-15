# EVOMTRS Static Website

Production-ready static marketing site for `https://evomtrs.com`.

## Structure

- `public/` HTML templates and static assets
- `scripts/convert-images.sh` approved EVOMTRS image conversion pipeline
- `scripts/render_site.py` env-driven site renderer
- `scripts/render-site.sh` local render wrapper
- `docker-compose.yml` container runtime on `shared_webnet`

## Environment

Copy `.env.example` to `.env` if you want a clean starting point, then fill in:

- `EVOMTRS_CONTACT_PHONE_E164`
- `EVOMTRS_CONTACT_PHONE_DISPLAY`
- `EVOMTRS_TEXT_PHONE_E164`
- `EVOMTRS_CONTACT_EMAIL`
- `EVOMTRS_ADDRESS_LINE1`
- `EVOMTRS_ZIP`
- `EVOMTRS_FORM_ENDPOINT`
- `EVOMTRS_LEGAL_UPDATED_DATE`
- `EVOMTRS_DIRECTIONS_URL`
- `EVOMTRS_MAP_EMBED_URL`

## Local Render

```bash
cd /root/evomtrs-site
./scripts/convert-images.sh
./scripts/render-site.sh
python3 -m http.server 8080 --directory dist
```

## npm Build Workflow

The site can also be built and served using npm:

```bash
cd /root/evomtrs-site
npm install
npm run build
npm run serve
```

Useful scripts:

- `npm run build` renders `public/` templates into `dist/`
- `npm run dev` renders and runs Cloudflare Pages local dev (`wrangler pages dev`)
- `npm run serve` renders and serves `dist/` locally on port `8080`
- `npm run cf:deploy` renders and deploys `dist/` with Wrangler

## Cloudflare Pages Setup

Use these project settings:

- Framework preset: `None`
- Build command: `npm run build`
- Build output directory: `dist`

Set these build-time environment variables in Cloudflare Pages:

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
- `EVOMTRS_FORM_ENDPOINT`
- `EVOMTRS_LEGAL_UPDATED_DATE`
- `EVOMTRS_DIRECTIONS_URL`
- `EVOMTRS_MAP_EMBED_URL`

## Docker

```bash
cd /root/evomtrs-site
docker compose up --build -d
```

The container serves rendered output on internal port `8080` and joins the external Docker network `shared_webnet` so Nginx Proxy Manager can forward `evomtrs.hidconsult.com` to it.
