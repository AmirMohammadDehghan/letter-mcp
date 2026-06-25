# معماری نهایی پروژه

## هدف پروژه

پروژه `letter-mcp` یک سرویس Django برای مدیریت قالب‌های DOCX و تولید نامه است. پنل مدیریت Django برای مدیریت templateها استفاده می‌شود و APIها برای کاربرهای احراز هویت‌شده و سرویس‌هایی مثل n8n قابل استفاده هستند.

## معماری Production

```text
User Browser
    |
    | HTTPS
    v
Arvan CDN / DNS
    |
    | HTTP Origin: 93.118.xxx.xxx:8002
    v
Docker Host / Ubuntu Server
    |
    | published port 8002 -> container port 8000
    v
Django + Gunicorn container
    |
    +--> PostgreSQL container
    |
    +--> RustFS/S3 storage
            ├── media bucket
            ├── static bucket
            └── backup bucket
```

## اجزای اصلی

| بخش | نقش |
|---|---|
| Django | اپلیکیشن اصلی، پنل admin، APIها |
| Gunicorn | اجرای WSGI در production |
| PostgreSQL | دیتابیس production |
| Docker Compose | اجرای web، db و backup service |
| Arvan CDN | HTTPS، DNS، CDN و اتصال به origin |
| RustFS/S3 | ذخیره media، static و backup |
| GitHub | منبع اصلی کد و جریان update deploy |

## Bucketهای پیشنهادی

```text
my-docgen-bucket          -> media files
static-docgen-bucket      -> static files
letter-mcp-backups        -> database backups
```

## نکته مهم static

در production با `DEBUG=0` و `Gunicorn`، Django به‌صورت پیش‌فرض `/static/` را سرو نمی‌کند. دو راه وجود دارد:

1. استفاده از WhiteNoise برای سرو static از خود کانتینر.
2. ارسال static به S3/RustFS و تنظیم `STATIC_URL` روی دامنه storage.

در معماری نهایی این پروژه، راه دوم انتخاب شده است:

```text
STATIC_URL=https://storage.24u.ir/static-docgen-bucket/static/
```

پس مرورگر باید فایل‌های admin را از `storage.24u.ir` بگیرد، نه از `/static/` روی دامنه اصلی.
