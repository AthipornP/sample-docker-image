#!/bin/sh
set -e

# Run migrations if DJANGO_MIGRATE=1
if [ "${DJANGO_MIGRATE:-1}" != "0" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput || true
fi

# Collect static if DJANGO_COLLECTSTATIC=1
if [ "${DJANGO_COLLECTSTATIC:-0}" = "1" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

exec "$@"
