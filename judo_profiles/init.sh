#!/usr/bin/env bash

if ! [[ -d "staticfiles" ]]
then
    python manage.py migrate
    python manage.py collectstatic
fi
python manage.py runserver 0.0.0.0:8000
