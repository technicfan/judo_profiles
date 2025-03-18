#!/usr/bin/env bash

if [[ -z $(ls "staticfiles") ]]
then
    python manage.py collectstatic
fi

python manage.py migrate
gunicorn --bind 0.0.0.0:8000 --workers 3 judo_profiles.wsgi:application
