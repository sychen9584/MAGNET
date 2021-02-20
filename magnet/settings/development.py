from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yr^4xctv2v5b0c%!ot6%sa644&$$ap6bvc5167*4ce50t66($v'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'magnet_db',
        'USER': 'magnet_admin',
        'PASSWORD': 'magnet',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Chicago'