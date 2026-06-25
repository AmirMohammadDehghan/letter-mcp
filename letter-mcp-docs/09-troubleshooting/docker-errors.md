# عیب‌یابی Docker و Gunicorn

## Worker failed to boot

لاگ نمونه:

```text
ModuleNotFoundError: No module named 'mcp.wsgi'
gunicorn.errors.HaltServer: Worker failed to boot
```

علت: مسیر WSGI اشتباه است.

در این پروژه درست است:

```text
core.wsgi:application
```

در Dockerfile یا compose نباید `mcp.wsgi:application` باشد.

## Permission denied برای volume

اگر سرویس به مسیر volume دسترسی ندارد:

```bash
sudo chown -R 1000:1000 ./some-volume
```

یا بسته به user داخل container بررسی کن.

## دیدن لاگ

```bash
docker compose logs -f web
docker compose logs --tail=100 db
docker compose ps
```

## پاکسازی و build دوباره

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

## تست داخل container

```bash
docker compose exec web pwd
docker compose exec web ls -lah /app
docker compose exec web python manage.py check
```
