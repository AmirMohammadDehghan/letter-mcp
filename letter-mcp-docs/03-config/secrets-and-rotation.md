# مدیریت Secretها و Rotate کردن کلیدها

## چرا مهم است؟

اگر `SECRET_KEY`، پسورد دیتابیس یا کلید S3 در چت، GitHub، لاگ یا فایل عمومی قرار بگیرد، باید آن را تغییر دهی.

## موارد حساس پروژه

```text
Django SECRET_KEY
PostgreSQL DB_PASSWORD
RustFS/S3 AWS_ACCESS_KEY_ID
RustFS/S3 AWS_SECRET_ACCESS_KEY
SSH password/private key
API keys داخل پروژه یا n8n
JWT secret اگر جدا باشد
```

## قوانین

- `.env` را commit نکن.
- فقط `.env.example` را با placeholder در Git نگه دار.
- پسوردها را در README ننویس.
- بعد از افشا شدن هر secret، آن را rotate کن.

## حذف .env از Git

اگر `.env` قبلاً track شده:

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking env file"
git push origin main
```

روی سرور، `.env` واقعی را نگه دار:

```bash
cp .env .env.server.backup
git pull origin main
cp .env.server.backup .env
```

## ساخت SECRET_KEY جدید Django

داخل کانتینر:

```bash
docker compose exec web python - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

مقدار خروجی را در `.env` بگذار:

```env
SECRET_KEY=NEW_SECRET
```

بعد:

```bash
docker compose restart web
```

## تغییر پسورد PostgreSQL

داخل PostgreSQL:

```bash
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME"
```

در psql:

```sql
ALTER USER lettermcp WITH PASSWORD 'NEW_STRONG_PASSWORD';
```

بعد `.env` را آپدیت کن:

```env
DB_PASSWORD=NEW_STRONG_PASSWORD
```

و restart:

```bash
docker compose restart web
```

## Rotate کلید RustFS/S3

در پنل RustFS یک access key جدید بساز، سپس `.env` را آپدیت کن:

```env
AWS_ACCESS_KEY_ID=NEW_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=NEW_SECRET_KEY
```

بعد:

```bash
docker compose restart web
```

و تست:

```bash
docker compose exec web python manage.py collectstatic --noinput -v 2
```
