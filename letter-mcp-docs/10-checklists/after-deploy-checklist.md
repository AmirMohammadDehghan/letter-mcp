# چک‌لیست بعد از هر آپدیت

- [ ] `git pull origin main` بدون خطا انجام شد.
- [ ] اگر migration جدید وجود دارد، `migrate` اجرا شد.
- [ ] اگر static تغییر کرده، `collectstatic` اجرا شد.
- [ ] web container restart شد.
- [ ] لاگ web بررسی شد.
- [ ] admin باز شد.
- [ ] APIهای مهم تست شدند.
- [ ] بکاپ بعد از deploy گرفته شد یا schedule فعال است.

دستورات:

```bash
cd /opt/apps/letter-mcp
git pull origin main
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
docker compose restart web
docker compose logs --tail=100 web
```

تست:

```bash
curl -I https://lettermcp.24u.ir/admin/
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```
