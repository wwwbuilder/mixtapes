web: gunicorn Mixtapes.wsgi
worker: python manage.py celery worker -E --maxtasksperchild=1000 --loglevel=info
