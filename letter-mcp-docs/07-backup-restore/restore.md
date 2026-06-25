# Restore دیتابیس PostgreSQL

## هشدار

Restore دیتابیس، دیتای فعلی را overwrite می‌کند. قبل از restore، از وضعیت فعلی بکاپ بگیر.

## 1. گرفتن بکاپ قبل از restore

```bash
cd /opt/apps/letter-mcp
bash scripts/backup-postgres-to-s3.sh
```

## 2. دانلود backup از S3

```bash
set -a
source .env
set +a
mkdir -p backups

aws --endpoint-url "$AWS_S3_ENDPOINT_URL" \
  s3 cp "s3://$BACKUP_S3_BUCKET/$BACKUP_S3_PREFIX/BACKUP_FILE.dump" \
  "backups/BACKUP_FILE.dump"
```

## 3. توقف web برای جلوگیری از write

```bash
docker compose stop web
```

## 4. restore

```bash
cat backups/BACKUP_FILE.dump | docker compose exec -T db pg_restore \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --clean \
  --if-exists \
  --no-owner
```

اگر متغیرها در host load نیستند:

```bash
set -a
source .env
set +a
```

## 5. اجرای migrate بعد از restore

```bash
docker compose start web
docker compose exec web python manage.py migrate
docker compose restart web
```

## 6. تست

```bash
curl -I https://lettermcp.24u.ir/admin/
docker compose logs --tail=100 web
```
