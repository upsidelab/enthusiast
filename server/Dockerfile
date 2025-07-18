FROM python:3.12

ARG PORT=8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=$PORT
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN apt-get update && apt-get install -y libpq-dev

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="/root/.local/bin:$PATH"

RUN /root/.local/bin/poetry install

COPY . .

RUN chmod u+x /app/docker-entrypoint.sh

EXPOSE $PORT

ENTRYPOINT ["/app/docker-entrypoint.sh"]