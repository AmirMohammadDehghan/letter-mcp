# دستورات روزمره Docker و Django

## وضعیت سرویس‌ها

```bash
cd /opt/apps/letter-mcp
docker compose ps
```

## لاگ‌ها

```bash
docker compose logs -f web
docker compose logs --tail=100 db
docker compose logs --tail=100 backup
```

## restart

```bash
docker compose restart web
```

## rebuild کامل

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

## migrate

```bash
docker compose exec web python manage.py migrate
```

## makemigrations

ترجیحاً روی سیستم dev انجام بده و migrationها را commit کن:

```bash
python manage.py makemigrations
git add api/migrations
git commit -m "Add api migrations"
git push origin main
```

روی سرور:

```bash
git pull origin main
docker compose exec web python manage.py migrate
```

## collectstatic

```bash
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```

## ساخت superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## بررسی تنظیمات Django داخل کانتینر

```bash
docker compose exec web python manage.py shell -c "
from django.conf import settings
from django.core.files.storage import storages
import os
print('DEBUG =', settings.DEBUG)
print('DEPLOY =', settings.DEPLOY)
print('USE_S3_STATIC env =', os.getenv('USE_S3_STATIC'))
print('USE_S3_STATIC settings =', getattr(settings, 'USE_S3_STATIC', None))
print('STATIC_URL =', settings.STATIC_URL)
print('staticfiles storage class =', storages['staticfiles'].__class__)
"
```
