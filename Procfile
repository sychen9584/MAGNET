web: gunicorn magnet.wsgi --log-file -
worker: celery -A magnet worker -l info --concurrency=10 -n worker1@%h
worker: celery -A magnet worker -l info --concurrency=10 -n worker2@%h
worker: celery -A magnet worker -l info --concurrency=10 -n worker3@%h
