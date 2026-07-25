#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth.models import User
import os
username = os.environ.get('ADMIN_USERNAME')
if username:
    User.objects.filter(username=username).update(is_staff=True, is_superuser=True)
"
