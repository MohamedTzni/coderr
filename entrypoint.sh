#!/bin/sh
set -e

echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -q; do
  sleep 1
done
echo "PostgreSQL ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
