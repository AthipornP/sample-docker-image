#!/bin/bash

# Wait for database to be ready (if using external DB)
# sleep 5

# Run database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear

# Start Django development server
python manage.py runserver 0.0.0.0:8000