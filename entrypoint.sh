#!/usr/bin/env bash

if [[ -z "$SECRET_KEY" ]]
then
    echo "SECRET_KEY is required - please add one"
    exit 1
fi

if [[ -n "$DATABASE_HOST" && -n "$DATABASE_PORT" ]]
then
    echo "waiting for database at $DATABASE_HOST:$DATABASE_PORT"
    while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do sleep 1; done;
elif ! [[ -d "data" ]]
then
    echo "No remote database given - falling back to sqlite"
    echo "make sure you configured a volume at /data if running with docker"
    mkdir data
fi

python manage.py migrate
exec uwsgi --http 0.0.0.0:"${APP_PORT:-8000}" uwsgi.ini
