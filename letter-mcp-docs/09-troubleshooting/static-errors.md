# عیب‌یابی static admin

## نشانه‌ها

### MIME type mismatch

```text
blocked due to MIME type (“text/html”) mismatch
X-Content-Type-Options: nosniff
```

یعنی مرورگر CSS/JS خواسته ولی HTML برگشته است.

### NS_ERROR_CORRUPTED_CONTENT

معمولاً وقتی CDN/سرور پاسخ نامناسب یا HTML برای فایل static می‌دهد رخ می‌دهد.

### CORS font error

```text
CORS header 'Access-Control-Allow-Origin' missing
```

یعنی فونت از دامنه storage لود شده ولی bucket هدر CORS نمی‌دهد.

## چک‌لیست اصلی

### 1. سرور چه STATIC_URL دارد؟

```bash
docker compose exec web python manage.py shell -c "from django.conf import settings; print(settings.STATIC_URL)"
```

در حالت S3 باید باشد:

```text
https://storage.24u.ir/static-docgen-bucket/static/
```

اگر `/static/` بود، یعنی `USE_S3_STATIC` یا settings.py درست نیست.

### 2. storage class چیست؟

```bash
docker compose exec web python manage.py shell -c "
from django.core.files.storage import storages
print(storages['staticfiles'].__class__)
"
```

در حالت S3 باید باشد:

```text
<class 'storages.backends.s3.S3Storage'>
```

### 3. فایل روی S3 هست؟

```bash
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

باید:

```text
200 OK
content-type: text/css
```

### 4. HTML admin چه لینک‌هایی تولید می‌کند؟

```bash
curl -s https://lettermcp.24u.ir/admin/login/ | grep -o "https://storage.24u.ir[^\"']*" | head
```

اگر چیزی برنگشت و HTML هنوز `/static/...` دارد، تنظیمات S3 static فعال نیست یا cache شده.

### 5. CORS فونت

```bash
curl -I \
  -H "Origin: https://lettermcp.24u.ir" \
  https://storage.24u.ir/static-docgen-bucket/static/jazzmin/fonts/vazirmatn/Vazirmatn-Regular.woff2
```

باید `access-control-allow-origin` داشته باشد.

## راه‌حل‌های رایج

### تنظیمات جدید داخل کانتینر نیست

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### bucket خالی است

```bash
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```

### کش Arvan مانده

در پنل Arvan purge کن:

```text
/admin/*
/static/*
/static-docgen-bucket/static/*
```
