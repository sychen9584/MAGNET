import os
from .base import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

# Heroku: Update database configuration from $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES = {'default':{}}
DATABASES['default'].update(db_from_env)

ALLOWED_HOSTS = ["blooming-peak-08320.herokuapp.com",
                    "magnet-winterlab.herokuapp.com"]

CELERY_BROKER_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Chicago'