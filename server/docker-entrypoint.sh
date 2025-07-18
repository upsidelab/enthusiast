#!/bin/sh

if [ "$RUN_WORKER" = "True" ]; then
    exec celery -A pecl.celery worker
else
    if [ "$RUN_MIGRATIONS" = "True" ]; then
        python manage.py migrate

        python manage.py ensuresuperuser --email=$ECL_ADMIN_EMAIL --password=$ECL_ADMIN_PASSWORD
    fi

    exec daphne -b 0.0.0.0 -p ${PORT:-8000} pecl.asgi:application
fi
