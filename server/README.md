# Enthusiast Server

This directory contains the server and the worker of Enthusiast. You can use it in API-only mode, or set up together with the [frontend](../frontend).

## Getting started

1. Install python3 (3.12+ recommended)
2. Install PostgreSQL together with pg_vector extension
3. Install Redis
4. Run `pip install -r requirements.txt`
5. Run `./manage.py migrate`
6. Run webserver `./manage.py runserver` and Celery `celery -A pecl.worker worker`
