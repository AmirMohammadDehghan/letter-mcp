# چک‌لیست هنگام خرابی

## 1. وضعیت سرویس‌ها

```bash
cd /opt/apps/letter-mcp
docker compose ps
docker compose logs --tail=150 web
```

## 2. تست origin

```bash
curl -I http://127.0.0.1:8002/admin/
curl -I http://SERVER_IP:8002/admin/ -H "Host: lettermcp.24u.ir"
```

## 3. تست دامنه

```bash
curl -I https://lettermcp.24u.ir/admin/
```

## 4. اگر 400 بود

- [ ] `ALLOWED_HOSTS` را چک کن.
- [ ] لاگ `Invalid HTTP_HOST` را ببین.

```bash
docker compose logs --tail=120 web | grep -i "Invalid HTTP_HOST" -A2 -B2
```

## 5. اگر static خراب بود

```bash
docker compose exec web python manage.py shell -c "from django.conf import settings; print(settings.STATIC_URL)"
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

## 6. اگر دیتابیس مشکل داشت

```bash
docker compose logs --tail=100 db
docker compose exec db pg_isready -U "$DB_USER" -d "$DB_NAME"
```

## 7. اگر deploy خراب شد

آخرین commit را ببین:

```bash
git log --oneline -5
```

rollback ساده:

```bash
git checkout PREVIOUS_COMMIT
docker compose up -d --build
```

بعداً برای برگشت به main:

```bash
git checkout main
git pull origin main
```
