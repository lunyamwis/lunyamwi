#!/bin/bash

# source /root/.local/share/virtualenvs/brooks-insurance-*/bin/activate

echo "<<<<<<<< Collect Staticfiles>>>>>>>>>"
python3 manage.py collectstatic --noinput


sleep 5
echo "<<<<<<<< Database Setup and Migrations Starts >>>>>>>>>"
# Run database migrations
# python3 manage.py makemigrations
python3 manage.py migrate &

sleep 5
echo "<<<<<<<<<<<<<<<<<<<< START API >>>>>>>>>>>>>>>>>>>>>>>>"
python3 manage.py runserver 0.0.0.0:8001
# Start the API with gunicorn
# gunicorn --bind 0.0.0.0:8000 setup.wsgi --reload --access-logfile '-' --workers=2
