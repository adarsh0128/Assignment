FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=esg_platform.settings.production

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY . .
RUN DJANGO_SECRET_KEY=build-only-collectstatic-secret \
    DJANGO_ALLOWED_HOSTS=localhost \
    DJANGO_SECURE_SSL_REDIRECT=false \
    python manage.py collectstatic --noinput

CMD ["sh", "-c", "gunicorn esg_platform.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
