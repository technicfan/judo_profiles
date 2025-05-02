#!/usr/bin/env bash

if [[ -z $(ls "staticfiles") ]]
then
    python manage.py collectstatic
fi
if [[ -f "nginx/nginx.conf" && -d "nginx_conf" ]]
then
    mv nginx/nginx.conf nginx_conf/default.conf
fi

python manage.py migrate
gunicorn --bind 0.0.0.0:8000 judo_profiles.wsgi
