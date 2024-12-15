#!/bin/sh

if [ "$RUN_WORKER" = "True" ]; then
    exec celery -A pecl.celery worker
else
    if [ "$RUN_MIGRATIONS" = "True" ]; then
        # TODO Make this a migration inside the server codebase
        apt-get update && apt-get install -y postgresql-client
        PGPASSWORD=$ECL_DB_PASSWORD psql -c "CREATE EXTENSION IF NOT EXISTS vector" -h $ECL_DB_HOST -p $ECL_DB_PORT -U $ECL_DB_USER $ECL_DB_NAME

        python manage.py migrate

        python manage.py ensuresuperuser --email=$ECL_ADMIN_EMAIL --password=$ECL_ADMIN_PASSWORD
    fi

    exec python manage.py runserver 0.0.0.0:${PORT:-8000}
fi
