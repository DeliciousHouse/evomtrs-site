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

## Docker

```bash
cd /root/evomtrs-site
docker compose up --build -d
```

The container serves rendered output on internal port `8080` and joins the external Docker network `shared_webnet` so Nginx Proxy Manager can forward `evomtrs.hidconsult.com` to it.
