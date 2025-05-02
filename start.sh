#!/usr/bin/env bash

if [[ -z $(ls "staticfiles") ]]
then
    python manage.py collectstatic
fi
if [[ -f "nginx/default.conf.template" && -d "nginx_conf" ]]
then
    mv nginx/default.conf.template nginx_conf/default.conf.template
fi

python manage.py migrate
gunicorn --bind 0.0.0.0:"$APP_PORT" judo_profiles.wsgi
