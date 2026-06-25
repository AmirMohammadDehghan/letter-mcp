# مرجع فایل .env سرور

فایل `.env` باید در ریشه پروژه روی سرور باشد:

```text
/opt/apps/letter-mcp/.env
```

این فایل نباید در Git commit شود.

## نمونه کامل production

> مقادیر حساس را با مقدار واقعی سرور خودت جایگزین کن. secrets واقعی را در مستندات، GitHub یا چت ذخیره نکن.

```env
DEBUG=0
DEPLOY=1

SECRET_KEY=CHANGE_ME_STRONG_DJANGO_SECRET

ALLOWED_HOSTS=lettermcp.24u.ir,SERVER_IP,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://lettermcp.24u.ir,http://SERVER_IP:8002

SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_SSL_REDIRECT=0

DB_NAME=lettermcp
DB_USER=lettermcp
DB_PASSWORD=CHANGE_ME_DB_PASSWORD
DB_HOST=db
DB_PORT=5432

USE_S3_MEDIA=1
USE_S3_STATIC=1

AWS_ACCESS_KEY_ID=CHANGE_ME_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=CHANGE_ME_SECRET_KEY
AWS_STORAGE_BUCKET_NAME=my-docgen-bucket
AWS_STATIC_BUCKET_NAME=static-docgen-bucket

AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=https://storage.24u.ir
AWS_S3_VERIFY=1
AWS_S3_ADDRESSING_STYLE=path
AWS_S3_SIGNATURE_VERSION=s3v4

S3_MEDIA_LOCATION=media
S3_STATIC_LOCATION=static

MEDIA_QUERYSTRING_AUTH=1
STATIC_QUERYSTRING_AUTH=0
AWS_QUERYSTRING_EXPIRE=86400

MEDIA_FILE_OVERWRITE=0
STATIC_FILE_OVERWRITE=1

BACKUP_S3_BUCKET=letter-mcp-backups
BACKUP_S3_PREFIX=postgres
BACKUP_RETENTION_DAYS=14
```

## توضیح متغیرها

| متغیر | توضیح |
|---|---|
| `DEBUG` | در production باید `0` باشد. |
| `DEPLOY` | اگر `1` باشد از PostgreSQL استفاده می‌شود. |
| `SECRET_KEY` | کلید امنیتی Django. باید قوی و محرمانه باشد. |
| `ALLOWED_HOSTS` | دامنه‌ها و IPهای مجاز برای Host header. |
| `CSRF_TRUSTED_ORIGINS` | originهای مجاز برای فرم‌های امن مثل login admin. |
| `DB_*` | تنظیمات اتصال به PostgreSQL container. |
| `USE_S3_MEDIA` | ارسال media به RustFS/S3. |
| `USE_S3_STATIC` | ارسال static به RustFS/S3 bucket جدا. |
| `AWS_STORAGE_BUCKET_NAME` | bucket فایل‌های media. |
| `AWS_STATIC_BUCKET_NAME` | bucket فایل‌های static. |
| `MEDIA_QUERYSTRING_AUTH` | signed URL برای media. برای فایل‌های حساس `1`. |
| `STATIC_QUERYSTRING_AUTH` | برای static باید `0` باشد. |
| `S3_MEDIA_LOCATION` | prefix فایل‌های media داخل bucket. |
| `S3_STATIC_LOCATION` | prefix فایل‌های static داخل bucket. |

## خطای رایج

این syntax اشتباه است و باید حذف شود:

```env
ENDPOINT: https://storage.24u.ir
```

فرمت درست `.env` همیشه این است:

```env
KEY=value
```
