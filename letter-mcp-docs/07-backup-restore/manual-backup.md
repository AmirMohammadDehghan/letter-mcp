# بکاپ دستی PostgreSQL و آپلود به S3

## بکاپ به فایل local

```bash
cd /opt/apps/letter-mcp
mkdir -p backups

TS=$(date +%Y%m%d-%H%M%S)
docker compose exec -T db pg_dump \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -Fc > "backups/letter-mcp-postgres-$TS.dump"
```

اگر متغیرها داخل shell نیستند:

```bash
set -a
source .env
set +a
```

## آپلود به S3 با awscli

```bash
set -a
source .env
set +a

aws --endpoint-url "$AWS_S3_ENDPOINT_URL" \
  s3 cp "backups/letter-mcp-postgres-$TS.dump" \
  "s3://$BACKUP_S3_BUCKET/${BACKUP_S3_PREFIX:-postgres}/letter-mcp-postgres-$TS.dump"
```

## بررسی فایل‌ها در S3

```bash
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" \
  s3 ls "s3://$BACKUP_S3_BUCKET/${BACKUP_S3_PREFIX:-postgres}/"
```

## بکاپ سریع یک‌خطی

```bash
cd /opt/apps/letter-mcp && set -a && source .env && set +a && mkdir -p backups && TS=$(date +%Y%m%d-%H%M%S) && docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "backups/letter-mcp-postgres-$TS.dump" && aws --endpoint-url "$AWS_S3_ENDPOINT_URL" s3 cp "backups/letter-mcp-postgres-$TS.dump" "s3://$BACKUP_S3_BUCKET/${BACKUP_S3_PREFIX:-postgres}/letter-mcp-postgres-$TS.dump"
```
