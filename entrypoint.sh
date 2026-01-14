#!/bin/bash

# source /root/.local/share/virtualenvs/brooks-insurance-*/bin/activate

echo "<<<<<<<< Collect Staticfiles>>>>>>>>>"
python3 manage.py collectstatic --noinput


# sleep 5
echo "<<<<<<<< Database Setup and Migrations Starts >>>>>>>>>"
# # Run database migrations
python3 manage.py makemigrations &
python3 manage.py migrate_schemas &


echo "<<<<<<<<<<<<<<<<<<<< START API >>>>>>>>>>>>>>>>>>>>>>>>"
gunicorn --bind 0.0.0.0:8000 core.wsgi:application