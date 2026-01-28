#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python mysite/manage.py migrate --noinput

# Collect static files (if needed)
# python mysite/manage.py collectstatic --noinput
