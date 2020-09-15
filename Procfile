release: python manage.py migrate
release: python manage.py loaddata fixtures.json
web: gunicorn todoapp.wsgi