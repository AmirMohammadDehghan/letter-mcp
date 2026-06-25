# پنل Admin و Superuser

## ساخت superuser

```bash
cd /opt/apps/letter-mcp
docker compose exec web python manage.py createsuperuser
```

بعد وارد شو:

```text
https://lettermcp.24u.ir/admin/
```

## ساخت superuser غیرتعاملی

```bash
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'CHANGE_ME_STRONG_PASSWORD')
    print('created')
else:
    print('already exists')
"
```

بعد از ورود، password را از پنل تغییر بده.

## تغییر password کاربر admin

```bash
docker compose exec web python manage.py changepassword admin
```

## مشکل admin بدون CSS

اگر admin بدون CSS است:

1. `STATIC_URL` را چک کن.
2. `collectstatic` را اجرا کن.
3. فایل static روی S3 را تست کن.
4. CORS فونت‌ها را تنظیم کن.

دستورات:

```bash
docker compose exec web python manage.py shell -c "from django.conf import settings; print(settings.STATIC_URL)"
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```
