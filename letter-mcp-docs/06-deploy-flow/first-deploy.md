# دیپلوی اولیه از صفر

## 1. کلون پروژه

```bash
cd /opt/apps
git clone git@github.com:AmirMohammadDehghan/letter-mcp.git
cd letter-mcp
```

## 2. ساخت فایل .env

```bash
cp .env.example .env
nano .env
```

مقادیر production را طبق `03-config/env-reference.md` کامل کن.

## 3. ساخت bucketها

در RustFS/S3 بساز:

```text
my-docgen-bucket
static-docgen-bucket
letter-mcp-backups
```

برای `static-docgen-bucket` دسترسی public read و CORS تنظیم کن.

## 4. build و up

```bash
docker compose up -d --build
```

## 5. بررسی سرویس‌ها

```bash
docker compose ps
docker compose logs --tail=100 web
```

## 6. migrate

معمولاً entrypoint اجرا می‌کند، ولی دستی هم می‌توانی بزنی:

```bash
docker compose exec web python manage.py migrate
```

## 7. collectstatic

```bash
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```

## 8. superuser

```bash
docker compose exec web python manage.py createsuperuser
```

## 9. تست‌ها

```bash
curl -I http://127.0.0.1:8002/admin/
curl -I http://SERVER_IP:8002/admin/ -H "Host: lettermcp.24u.ir"
curl -I https://lettermcp.24u.ir/admin/
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

## 10. ورود به admin

```text
https://lettermcp.24u.ir/admin/
```
