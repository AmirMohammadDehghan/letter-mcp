# Migration و Static

## هشدار migration

اگر لاگ گفت:

```text
Your models in app(s): 'api' have changes that are not yet reflected in a migration
```

یعنی مدل‌ها تغییر کرده‌اند ولی migration ساخته نشده است.

## مسیر درست

روی سیستم توسعه:

```bash
python manage.py makemigrations
python manage.py migrate

git add api/migrations
git commit -m "Add missing api migrations"
git push origin main
```

روی سرور:

```bash
cd /opt/apps/letter-mcp
git pull origin main
docker compose exec web python manage.py migrate
```

## collectstatic روی S3

اگر `USE_S3_STATIC=1` باشد، collectstatic باید روی S3 برود:

```bash
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```

بررسی تنظیمات:

```bash
docker compose exec web python manage.py shell -c "
from django.conf import settings
from django.core.files.storage import storages
print(settings.STATIC_URL)
print(storages['staticfiles'].__class__)
"
```

خروجی درست:

```text
https://storage.24u.ir/static-docgen-bucket/static/
<class 'storages.backends.s3.S3Storage'>
```
