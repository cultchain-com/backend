#!/bin/bash -xe

python manage.py makemigrations user_profile
python manage.py migrate

python manage.py makemigrations indexer
python manage.py migrate indexer

python manage.py makemigrations contract_parser
python manage.py migrate

python manage.py makemigrations miscellaneous
python manage.py migrate

python manage.py makemigrations blog
python manage.py migrate

python manage.py collectstatic --no-input --clear

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL || true
else
    echo "No superusername found"
fi

$@
gunicorn cultchian_backend.wsgi:application --bind 0.0.0.0:8000
#python manage.py runserver 0.0.0.0:8000
