#!/bin/sh
# Container entrypoint: prepare the database and static files, then start the web server.
set -e

python manage.py migrate --noinput

# Create the admin account on first start (DJANGO_SUPERUSER_PASSWORD is read from the env)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null \
        && echo "Admin account created: $DJANGO_SUPERUSER_EMAIL" \
        || echo "Admin account already exists: $DJANGO_SUPERUSER_EMAIL"
fi

# Public port for visitors, plus 127.0.0.1:8000 so the demo portal URLs in
# universities_deadlines.xlsx resolve inside the container during auto-apply.
# Several threads are needed: an auto-apply request waits while the headless
# browser loads demo portal pages from this same server.
exec gunicorn aikapply.wsgi:application \
    --bind "0.0.0.0:${PORT:-7860}" \
    --bind 127.0.0.1:8000 \
    --workers "${WEB_WORKERS:-2}" --threads 4 --timeout 300
