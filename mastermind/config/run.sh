#!/bin/bash

# Wait for postgresql container
/wait-for.sh postgres 5432

# Migrate database and collectstatic
python manage.py collectstatic --noinput

# Run gunicorn for django server
gunicorn mastermind.wsgi -b 0.0.0.0:8001 --reload
