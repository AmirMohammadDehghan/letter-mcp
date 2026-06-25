# مدیریت static و media روی S3/RustFS

## هدف

- `media` شامل فایل‌های داینامیک است: آپلودها، قالب‌های DOCX، خروجی نامه‌ها.
- `static` شامل فایل‌های ثابت است: Django admin، jazzmin، css/js/fonts.

## تنظیمات env

```env
USE_S3_MEDIA=1
USE_S3_STATIC=1

AWS_STORAGE_BUCKET_NAME=my-docgen-bucket
AWS_STATIC_BUCKET_NAME=static-docgen-bucket

S3_MEDIA_LOCATION=media
S3_STATIC_LOCATION=static

MEDIA_QUERYSTRING_AUTH=1
STATIC_QUERYSTRING_AUTH=0
```

## رفتار نهایی

`collectstatic` باید فایل‌ها را به این مسیرها بفرستد:

```text
static-docgen-bucket/static/admin/css/base.css
static-docgen-bucket/static/admin/js/theme.js
static-docgen-bucket/static/jazzmin/...
```

URL نهایی static باید شبیه این باشد:

```text
https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

اگر صفحه admin هنوز این را می‌زند:

```text
https://lettermcp.24u.ir/static/admin/css/base.css
```

یعنی `STATIC_URL` روی سرور هنوز S3 نشده است.

## تست collectstatic

```bash
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```

بعد:

```bash
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

خروجی درست:

```text
HTTP/2 200
content-type: text/css
```

## تست HTML admin

```bash
curl -s https://lettermcp.24u.ir/admin/login/ | grep -o "https://storage.24u.ir[^\"']*" | head
```

باید لینک‌های static از `storage.24u.ir` بیایند.
