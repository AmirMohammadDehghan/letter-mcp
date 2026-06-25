# جریان آپدیت دیپلوی

## مسیر استاندارد

روی سیستم توسعه:

```bash
git status
python manage.py makemigrations
python manage.py test

git add .
git commit -m "Describe changes"
git push origin main
```

روی سرور:

```bash
cd /opt/apps/letter-mcp
git pull origin main
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
docker compose restart web
```

## اگر تغییرات Dockerfile یا requirements مهم بود

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

## تست بعد از آپدیت

```bash
docker compose ps
docker compose logs --tail=80 web
curl -I https://lettermcp.24u.ir/admin/
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

## اگر Arvan کش کرده بود

در Arvan cache purge کن:

```text
/admin/*
/static/*
/static-docgen-bucket/static/*
```
