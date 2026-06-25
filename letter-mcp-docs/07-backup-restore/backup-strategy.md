# استراتژی بکاپ و Restore

## چه چیزهایی باید بکاپ شوند؟

| داده | محل | روش بکاپ |
|---|---|---|
| PostgreSQL database | Docker volume `postgres_data` | `pg_dump` و upload به S3 |
| media files | `my-docgen-bucket` | خود S3 منبع اصلی است؛ lifecycle/versioning پیشنهاد می‌شود |
| static files | `static-docgen-bucket` | قابل بازسازی با `collectstatic` است |
| `.env` | سرور | بکاپ امن و رمزنگاری‌شده دستی |
| کد پروژه | GitHub | Git repository |

## اولویت‌ها

1. دیتابیس مهم‌ترین بخش است.
2. media اگر فقط روی S3 است، باید bucket policy/lifecycle و backup جدا داشته باشد.
3. static قابل بازسازی است و نیاز به بکاپ جدی ندارد.
4. `.env` باید امن نگهداری شود؛ بدون آن restore سخت می‌شود.

## نام‌گذاری فایل backup

```text
letter-mcp-postgres-YYYYmmdd-HHMMSS.dump
```

مثال:

```text
letter-mcp-postgres-20260625-031500.dump
```

## retention پیشنهادی

```text
روزانه: 14 روز اخیر
هفتگی: 8 هفته اخیر
ماهانه: 12 ماه اخیر
```

نسخه ساده فعلی:

```env
BACKUP_RETENTION_DAYS=14
```
