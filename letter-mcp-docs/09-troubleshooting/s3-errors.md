# عیب‌یابی S3/RustFS

## bucket خالی مانده

اگر collectstatic روی سرور گفت:

```text
copied to '/app/staticfiles'
```

یعنی static هنوز local است، نه S3.

بررسی:

```bash
docker compose exec web python manage.py shell -c "
from django.conf import settings
from django.core.files.storage import storages
import os
print(os.getenv('USE_S3_STATIC'))
print(getattr(settings, 'USE_S3_STATIC', None))
print(settings.STATIC_URL)
print(storages['staticfiles'].__class__)
"
```

## USE_S3_STATIC env هست ولی settings ندارد

خطا:

```text
AttributeError: 'Settings' object has no attribute 'USE_S3_STATIC'
```

یعنی `settings.py` داخل container نسخه قدیمی است یا فایل هنوز اصلاح نشده.

راه‌حل:

```bash
grep -n "USE_S3_STATIC" core/settings.py
docker compose build --no-cache web
docker compose up -d
```

## 403 روی فایل static

علت:

- bucket public نیست.
- `STATIC_QUERYSTRING_AUTH=1` است.
- ACL object درست نیست.

برای static:

```env
STATIC_QUERYSTRING_AUTH=0
```

## 404 روی فایل static

علت:

- collectstatic اجرا نشده.
- prefix اشتباه است.
- bucket اشتباه است.

تست:

```bash
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

## CORS missing

CORS را طبق `05-storage-s3-rustfs/cors.md` تنظیم کن و cache را purge کن.
