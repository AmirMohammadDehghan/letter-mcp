# سرویس تولید نامه با Django، JWT، n8n و RustFS

این پروژه یک سرویس امن برای تولید نامه‌های DOCX از روی قالب‌های قابل مدیریت در پنل ادمین است.

## ایده اصلی

1. ادمین هر حساب در پنل Django قالب DOCX نامه را ثبت می‌کند.
2. برای هر قالب یک `key` ثابت تعریف می‌شود؛ n8n با همین `key` قالب را صدا می‌زند.
3. n8n با JWT احراز هویت می‌کند و فقط قالب‌های همان اکانت را می‌بیند.
4. API از روی قالب و `variables` یک نامه جدید می‌سازد.
5. فایل خروجی در storage پیش‌فرض ذخیره می‌شود؛ در production این storage می‌تواند RustFS/S3 باشد.
6. API لینک دانلود، مسیر ذخیره، شناسه نامه، سازنده و اطلاعات audit را برمی‌گرداند.
7. برای جلوگیری از تولید تکراری در retryهای n8n، `idempotency_key` پشتیبانی می‌شود.

## معماری داده

### DocumentTemplate

هر قالب متعلق به یک کاربر/اکانت است.

فیلدهای مهم:

- `owner`: مالک قالب
- `name`: نام نمایشی فارسی
- `key`: کد پایدار برای n8n، مثل `introduction-letter`
- `template_file`: فایل DOCX قالب
- `required_fields`: فیلدهای اجباری ورودی
- `sample_variables`: نمونه داده برای راهنمای n8n
- `is_active`: فقط قالب‌های فعال از API دیده می‌شوند

### GeneratedDocument

هر نامه تولیدشده با audit کامل ذخیره می‌شود.

فیلدهای مهم:

- `owner`: مالک نامه
- `created_by`: کاربری که نامه را ساخته است
- `template`: قالب استفاده‌شده
- `variables`: داده‌های ورودی
- `meta`: اطلاعات جانبی مانند workflow name یا execution id از n8n
- `idempotency_key`: جلوگیری از تولید تکراری
- `source`: منبع ساخت، مثل `n8n`
- `status`: وضعیت تولید
- `output_file`: فایل خروجی DOCX

## نصب

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## تنظیم RustFS برای media

در production این بخش از `.env` را تنظیم کن:

```env
USE_S3_MEDIA=1
AWS_ACCESS_KEY_ID=admin_24u
AWS_SECRET_ACCESS_KEY=YOUR_RUSTFS_SECRET
AWS_STORAGE_BUCKET_NAME=django-media
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=https://storage.24u.ir
AWS_QUERYSTRING_AUTH=1
AWS_QUERYSTRING_EXPIRE=86400
AWS_S3_VERIFY=1
S3_MEDIA_LOCATION=media
```

پیشنهاد امنیتی: bucket را private نگه دار و اجازه بده Django لینک signed تولید کند.

## احراز هویت JWT

### دریافت توکن

```bash
curl -X POST "https://catalogue.24u.ir/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"n8n-account","password":"your-password"}'
```

خروجی:

```json
{
  "access": "...",
  "refresh": "..."
}
```

### استفاده از access token

```bash
curl "https://catalogue.24u.ir/api/templates/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### refresh token

```bash
curl -X POST "https://catalogue.24u.ir/api/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"REFRESH_TOKEN"}'
```

## Endpointها

### تست کاربر فعلی

```http
GET /api/me/
Authorization: Bearer ACCESS_TOKEN
```

### لیست قالب‌های قابل استفاده

```http
GET /api/templates/
Authorization: Bearer ACCESS_TOKEN
```

خروجی نمونه:

```json
{
  "status": "success",
  "templates": [
    {
      "id": 1,
      "name": "نامه معرفی",
      "key": "introduction-letter",
      "required_fields": ["recipient_name", "subject"],
      "sample_variables": {
        "recipient_name": "شرکت نمونه",
        "subject": "معرفی جهت همکاری"
      },
      "is_active": true
    }
  ]
}
```

### تولید نامه

```http
POST /api/generate/
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

Body:

```json
{
  "template_key": "introduction-letter",
  "variables": {
    "recipient_name": "شرکت نمونه",
    "subject": "معرفی جهت همکاری"
  },
  "meta": {
    "workflow": "letter-generator",
    "execution_id": "12345"
  },
  "idempotency_key": "n8n-execution-12345",
  "source": "n8n"
}
```

خروجی موفق:

```json
{
  "status": "success",
  "reused": false,
  "document": {
    "id": 10,
    "status": "success",
    "source": "n8n",
    "template_key": "introduction-letter",
    "template_name": "نامه معرفی",
    "storage_key": "media/generated/user_1/introduction-letter/introduction-letter-10-a1b2c3d4e5.docx",
    "download_url": "https://storage.24u.ir/django-media/media/generated/...",
    "created_at": "2026-06-23T12:00:00+03:30"
  }
}
```

اگر همان `idempotency_key` دوباره ارسال شود، API همان نامه قبلی را برمی‌گرداند:

```json
{
  "status": "success",
  "reused": true,
  "document": {
    "id": 10
  }
}
```

### لیست نامه‌های ساخته‌شده

```http
GET /api/documents/
Authorization: Bearer ACCESS_TOKEN
```

فیلترهای قابل استفاده:

- `template_key`
- `status`
- `idempotency_key`

برای staff/superuser:

```http
GET /api/documents/?scope=all
```

### جزئیات یک نامه

```http
GET /api/documents/10/
Authorization: Bearer ACCESS_TOKEN
```

## اتصال n8n

### مرحله ۱: گرفتن JWT

HTTP Request Node:

- Method: `POST`
- URL: `https://catalogue.24u.ir/api/auth/token/`
- Body Type: JSON

```json
{
  "username": "n8n-account",
  "password": "your-password"
}
```

access token را ذخیره کن.

### مرحله ۲: گرفتن لیست قالب‌ها

- Method: `GET`
- URL: `https://catalogue.24u.ir/api/templates/`
- Header:

```text
Authorization: Bearer {{$json.access}}
```

### مرحله ۳: تولید نامه

- Method: `POST`
- URL: `https://catalogue.24u.ir/api/generate/`
- Header:

```text
Authorization: Bearer ACCESS_TOKEN
Content-Type: application/json
```

Body نمونه:

```json
{
  "template_key": "introduction-letter",
  "variables": {
    "recipient_name": "{{$json.recipient_name}}",
    "subject": "{{$json.subject}}"
  },
  "meta": {
    "workflow": "letter-generator",
    "execution_id": "{{$execution.id}}"
  },
  "idempotency_key": "{{$execution.id}}",
  "source": "n8n"
}
```

### مرحله ۴: دانلود فایل

از `document.download_url` استفاده کن.

## نکات امنیتی

- `.env`، `db.sqlite3` و `media/` نباید وارد Git شوند.
- برای هر n8n یک user جدا بساز تا دسترسی قالب‌ها account-scoped باشد.
- access token را کوتاه‌مدت نگه دار و در n8n از refresh token استفاده کن.
- bucket RustFS را private نگه دار.
- پنل RustFS را عمومی نکن؛ فقط API storage عمومی/پروکسی باشد.

## اجرای تست‌ها

```bash
python manage.py test
```

تست‌ها موارد مهم زیر را پوشش می‌دهند:

- عدم دسترسی بدون JWT
- محدود بودن لیست قالب‌ها به owner
- تولید نامه موفق
- جلوگیری از تولید تکراری با `idempotency_key`
- عدم امکان استفاده از قالب اکانت دیگر
- مشاهده کل نامه‌ها فقط برای staff با `scope=all`

## احراز هویت Service API Key برای n8n

برای اتصال n8n لازم نیست هر بار username/password یا JWT استفاده شود. این پروژه علاوه بر JWT، از کلید سرویس مخصوص ماشین‌به‌ماشین هم پشتیبانی می‌کند.

### چرا API Key برای n8n بهتر است؟

- n8n فقط یک کلید امن ذخیره می‌کند.
- username/password کاربر در هر execution استفاده نمی‌شود.
- هر کلید به یک `owner` وصل است؛ بنابراین قالب‌ها و نامه‌ها همچنان فقط برای همان اکانت دیده می‌شوند.
- کلید خام در دیتابیس ذخیره نمی‌شود؛ فقط hash آن ذخیره می‌شود.
- کلید قابل غیرفعال‌سازی، تاریخ انقضا و محدودیت source دارد.
- `last_used_at` در پنل ادمین ثبت می‌شود.

### ساخت API Key برای n8n

اول مطمئن شو user مخصوص n8n را ساخته‌ای:

```bash
python manage.py createsuperuser
# یا از پنل admin یک user معمولی بساز
```

بعد برای آن user یک کلید بساز:

```bash
python manage.py create_service_api_key \
  --owner n8n-account \
  --name "n8n production" \
  --source n8n
```

خروجی شبیه این است:

```text
Service API key created successfully.
Owner: n8n-account
Name: n8n production
Prefix: n8n_AbCdEf1

Copy this raw key now. It will never be shown again:
n8n_AbCdEf123456789...
```

کلید خام را همان لحظه کپی کن و در n8n Credentials یا متغیر امن نگه دار. بعداً از دیتابیس قابل بازیابی نیست.

اگر تاریخ انقضا می‌خواهی:

```bash
python manage.py create_service_api_key \
  --owner n8n-account \
  --name "n8n production" \
  --source n8n \
  --expires-days 365
```

### استفاده در n8n

برای همه APIها می‌توانی به جای JWT این header را بفرستی:

```http
X-API-Key: n8n_xxxxxxxxxxxxxxxxx
```

یا این مدل:

```http
Authorization: Api-Key n8n_xxxxxxxxxxxxxxxxx
```

### لیست قالب‌ها با API Key

```bash
curl "https://catalogue.24u.ir/api/templates/" \
  -H "X-API-Key: n8n_xxxxxxxxxxxxxxxxx"
```

### تولید نامه با API Key

```bash
curl -X POST "https://catalogue.24u.ir/api/generate/" \
  -H "X-API-Key: n8n_xxxxxxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "template_key": "introduction-letter",
    "variables": {
      "recipient_name": "شرکت نمونه",
      "subject": "معرفی جهت همکاری"
    },
    "idempotency_key": "n8n-execution-12345",
    "source": "n8n",
    "meta": {
      "workflow": "letter-generator",
      "execution_id": "12345"
    }
  }'
```

اگر کلید را با `--source n8n` ساخته باشی و در body مقدار `source` چیز دیگری مثل `api` بفرستی، درخواست `403` می‌گیرد. این برای جلوگیری از سوءاستفاده از کلیدهای مخصوص n8n است.

### مدیریت کلیدها در Admin

در پنل ادمین مدل «کلیدهای API سرویس» را می‌بینی. از آنجا می‌توانی:

- کلید را فعال/غیرفعال کنی.
- تاریخ انقضا را ببینی یا تغییر دهی.
- owner کلید را بررسی کنی.
- زمان آخرین استفاده را ببینی.

کلید خام از admin قابل مشاهده نیست؛ فقط `key_prefix` نمایش داده می‌شود.
