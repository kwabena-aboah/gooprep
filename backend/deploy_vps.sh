#!/usr/bin/env bash
# Gooprep Backend — Namecheap VPS Deploy (Ubuntu 22.04)
set -e
PROJECT_DIR="/var/www/gooprep/backend"
VENV_DIR="$PROJECT_DIR/.venv"
DOMAIN="api.gooprep.com"

echo "=== Gooprep Backend VPS Deployment ==="
apt-get update -q
apt-get install -y -q python3.11 python3.11-venv python3-pip postgresql postgresql-contrib \
  nginx redis-server supervisor certbot python3-certbot-nginx git curl

sudo -u postgres psql -c "CREATE USER gooprep WITH PASSWORD 'change_this_password';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE gooprep OWNER gooprep;" 2>/dev/null || true

mkdir -p $PROJECT_DIR
python3.11 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip && pip install -r $PROJECT_DIR/requirements.txt

cd $PROJECT_DIR
if [ ! -f ".env" ]; then cp .env.example .env; echo "⚠️  Edit $PROJECT_DIR/.env before continuing!"; exit 1; fi
python manage.py migrate --noinput
python manage.py collectstatic --noinput

cat > /etc/nginx/sites-available/gooprep-api << NGINX
server {
    listen 80; server_name $DOMAIN;
    client_max_body_size 50M;
    location /static/ { alias $PROJECT_DIR/staticfiles/; expires 1y; }
    location /media/  { alias $PROJECT_DIR/media/; expires 30d; }
    location /ws/ {
        proxy_pass http://127.0.0.1:8001; proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade; proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host; proxy_read_timeout 86400;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$http_host; proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX
ln -sf /etc/nginx/sites-available/gooprep-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

cat > /etc/supervisor/conf.d/gooprep.conf << SUPERVISOR
[program:gooprep-gunicorn]
command=$VENV_DIR/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 120
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gooprep/gunicorn.err.log
stdout_logfile=/var/log/gooprep/gunicorn.out.log

[program:gooprep-daphne]
command=$VENV_DIR/bin/daphne -b 127.0.0.1 -p 8001 config.asgi:application
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gooprep/daphne.err.log
stdout_logfile=/var/log/gooprep/daphne.out.log

[program:gooprep-celery]
command=$VENV_DIR/bin/celery -A config worker --loglevel=info --concurrency=4
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gooprep/celery.err.log
stdout_logfile=/var/log/gooprep/celery.out.log

[group:gooprep]
programs=gooprep-gunicorn,gooprep-daphne,gooprep-celery
SUPERVISOR

mkdir -p /var/log/gooprep && chown -R www-data /var/log/gooprep
supervisorctl reread && supervisorctl update && supervisorctl restart gooprep:*
echo "✅ Backend deployed at http://$DOMAIN"
echo "   Health: curl http://$DOMAIN/api/health/"
