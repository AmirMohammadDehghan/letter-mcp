# Bucketهای RustFS/S3

## Bucketهای پیشنهادی

| bucket | کاربرد | دسترسی پیشنهادی |
|---|---|---|
| `my-docgen-bucket` | فایل‌های media مثل templateها و خروجی‌ها | private یا signed URL |
| `static-docgen-bucket` | فایل‌های static مثل admin css/js، jazzmin و fonts | public read |
| `letter-mcp-backups` | بکاپ دیتابیس PostgreSQL | private |

## ساخت bucketها

از پنل RustFS یا با ابزار `mc`:

```bash
mc alias set rustfs https://storage.24u.ir ACCESS_KEY SECRET_KEY
mc mb rustfs/my-docgen-bucket
mc mb rustfs/static-docgen-bucket
mc mb rustfs/letter-mcp-backups
```

## دسترسی public برای static

static باید توسط مرورگر بدون signed URL خوانده شود. بنابراین:

```env
STATIC_QUERYSTRING_AUTH=0
```

و bucket یا objectهای static باید public read باشند.

## media private

برای media اگر فایل‌ها حساس‌اند:

```env
MEDIA_QUERYSTRING_AUTH=1
```

در این حالت URLها signed می‌شوند و محدودیت زمانی دارند:

```env
AWS_QUERYSTRING_EXPIRE=86400
```
