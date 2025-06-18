FROM python:3.12

ARG PORT=8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=$PORT

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y libpq-dev

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install daphne

COPY . .

RUN chmod u+x /app/docker-entrypoint.sh

EXPOSE $PORT

ENTRYPOINT ["/app/docker-entrypoint.sh"]