# production.py

import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Required environment variables for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')

if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST]):
    raise ValueError(
        "Database environment variables must be set in production: "
        "DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'