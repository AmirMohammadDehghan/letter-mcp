# Dockerfile و entrypoint

## Dockerfile پیشنهادی

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
```

## نکته مهم wsgi

قبلاً خطا داشتیم:

```text
ModuleNotFoundError: No module named 'mcp.wsgi'
```

مسیر درست برای این پروژه:

```text
core.wsgi:application
```

نه:

```text
mcp.wsgi:application
```

## entrypoint.sh پیشنهادی

```sh
#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
exec "$@"
```

اگر static روی S3 است، همین `collectstatic` فایل‌ها را به bucket می‌فرستد؛ به شرطی که `settings.py` و `.env` درست باشند.

## requirements.txt

حداقل پکیج‌های مرتبط:

```txt
Django
psycopg[binary]
gunicorn
python-dotenv
djangorestframework
djangorestframework-simplejwt
django-storages
boto3
```

اگر از WhiteNoise fallback استفاده می‌کنی:

```txt
whitenoise
```
