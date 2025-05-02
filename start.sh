#!/usr/bin/env bash

if [[ -f "nginx/default.conf.template" && -d "nginx_conf" ]]
then
    mv nginx/default.conf.template nginx_conf/default.conf.template
fi

if [[ -z $(ls "staticfiles") ]]
then
    python manage.py collectstatic
fi

while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do sleep 1; done;

python manage.py migrate
gunicorn --bind 0.0.0.0:"$APP_PORT" judo_profiles.wsgi
