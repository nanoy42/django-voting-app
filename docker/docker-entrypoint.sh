#!/usr/bin/env bash
set -euo pipefail

cat local_settings.template.py | envsubst > django_voting_app/local_settings.py

AUTOMIGRATE=${AUTOMIGRATE:-yes}

if [ "$AUTOMIGRATE" != "skip" ]; then
  python3 manage.py migrate --noinput
fi

# https://pythonspeed.com/articles/gunicorn-in-docker/
gunicorn --worker-tmp-dir /dev/shm --workers=2 --threads=4 --worker-class=gthread --log-file=- django_voting_app.wsgi -b 0.0.0.0:8000
