#!/bin/sh

if [ "$RUN_WORKER" = "True" ]; then
    exec celery -A pecl.celery worker --loglevel=info -E
else
    if [ "$RUN_MIGRATIONS" = "True" ]; then
        python manage.py migrate

        python manage.py ensuresuperuser --email=$ECL_ADMIN_EMAIL --password=$ECL_ADMIN_PASSWORD
    fi

    exec python manage.py runserver 0.0.0.0:$PORT
fi
