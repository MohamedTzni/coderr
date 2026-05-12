#!/bin/sh
set -e

echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -q; do
  sleep 1
done
echo "PostgreSQL ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create guest users if they don't exist
python manage.py shell << END
from django.contrib.auth.models import User
from profiles_app.models import UserProfile

if not User.objects.filter(username='guest').exists():
    guest_user = User.objects.create_user(
        username='guest',
        email='guest@coderr.local',
        password='guest'
    )
    UserProfile.objects.create(
        user=guest_user,
        type='customer',
        email='guest@coderr.local'
    )
    print('Guest customer user created')

if not User.objects.filter(username='guest_business').exists():
    guest_biz = User.objects.create_user(
        username='guest_business',
        email='guest_business@coderr.local',
        password='guest'
    )
    UserProfile.objects.create(
        user=guest_biz,
        type='business',
        email='guest_business@coderr.local'
    )
    print('Guest business user created')
END

exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
