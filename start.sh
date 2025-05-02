#!/usr/bin/env bash

if [[ -n "$DATABASE_HOST" && -n "$DATABASE_PORT" ]]
then
    echo "waiting for database at $DATABASE_HOST:$DATABASE_PORT"
    while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do sleep 1; done;
elif ! [[ -d "data" ]]
then
    mkdir data
fi

python manage.py migrate
exec uwsgi --http 0.0.0.0:"$APP_PORT" uwsgi.ini
