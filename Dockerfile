FROM nginx:1.27-alpine

RUN apk add --no-cache python3

COPY public /opt/evomtrs/public
COPY scripts/render_site.py /opt/evomtrs/render_site.py
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /docker-entrypoint.d /opt/evomtrs/runtime

COPY <<'EOF' /docker-entrypoint.d/40-render-site.sh
#!/bin/sh
set -eu
python3 /opt/evomtrs/render_site.py /opt/evomtrs/public /usr/share/nginx/html
EOF

RUN chmod +x /docker-entrypoint.d/40-render-site.sh

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
