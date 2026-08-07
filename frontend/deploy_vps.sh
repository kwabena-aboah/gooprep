#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  Gooprep Frontend — Namecheap VPS Deployment Script
#  Ubuntu 22.04 | Nginx static hosting
#  Run from /var/www/gooprep/frontend after pushing code
# ─────────────────────────────────────────────────────────────────
set -e

FRONTEND_DIR="/var/www/gooprep/frontend"
DIST_DIR="$FRONTEND_DIR/dist"
NGINX_CONF="/etc/nginx/sites-available/gooprep-frontend"
DOMAIN="gooprep.com"

echo "=== Gooprep Frontend VPS Deployment ==="

# 1. Install Node.js 20 if needed
if ! command -v node &>/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

# 2. Install dependencies and build
cd $FRONTEND_DIR
npm install
npm run build
echo "✅ Build complete — output in $DIST_DIR"

# 3. Nginx config (SPA — all routes serve index.html)
cat > $NGINX_CONF << NGINX
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    root $DIST_DIR;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;
    gzip_min_length 1000;

    # Long cache for hashed assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # No cache for index.html (always get the latest app shell)
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # Proxy API calls to Django backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Proxy WebSocket to Daphne
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }

    # Proxy media files
    location /media/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host;
    }
}
NGINX

ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "✅ Nginx reloaded"

# 4. SSL (uncomment after DNS is live)
# certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@gooprep.com
# echo "✅ SSL certificate issued"

echo ""
echo "✅ Frontend deployed at http://$DOMAIN"
echo "   API: http://$DOMAIN/api/health/"
