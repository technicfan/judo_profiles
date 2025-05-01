#!/usr/bin/env bash

if [[ -z $(ls "staticfiles") ]]
then
    python manage.py collectstatic
fi
if ! [[ -f "nginx_conf/nginx.conf" ]]
then
    cp nginx/nginx.conf nginx_conf/nginx.conf
fi

python manage.py migrate
gunicorn --bind 0.0.0.0:8000 --workers 3 judo_profiles.wsgi:application
