"""
Django settings for finances project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fm^*_5m)ug!kw=dp3ahqs$_$majt7ch8rblh@5h@39g(dtc7(p'

# SECURITY WARNING: don't run with debug turned on in production!
import os

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ledger',
)

# Django requires a list of hosts this site is served from; since users can
# add new hosts with Pony at any time, we just trust SERVER_NAME (set by
# Apache) to be the correct hostname. If you want to restrict which virtual
# hosts your application can run on, disable this middleware and set
# ALLOWED_HOSTS by hand.
class AllowedHostsMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response
    def process_request(self, request):
        # Django 1.6
        global ALLOWED_HOSTS
        name = request.META.get('SERVER_NAME')
        if name and name not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(name)
    def __call__(self, request):
        # Django 1.11+
        self.process_request(request)
        return self.get_response(request)
MIDDLEWARE_CLASSES = (
    'finances.settings.AllowedHostsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'finances.urls'

WSGI_APPLICATION = 'finances.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file' : os.path.expanduser('~/.my.cnf'),
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'NAME': 'alahi+alahi',
    }
}

LOGIN_URL ='/signin/'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/__scripts/django/static/'
