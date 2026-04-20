#!/bin/sh
python manage.py migrate
python manage.py installwatson
python manage.py buildwatson
python manage.py collectstatic --noinput
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000