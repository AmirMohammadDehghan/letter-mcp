# بکاپ خودکار

دو روش پیشنهادی وجود دارد:

1. سرویس `backup` داخل Docker Compose.
2. cron روی host.

## روش 1: backup service در Docker Compose

فایل `scripts/backup-postgres-to-s3.sh` را قابل اجرا کن:

```bash
chmod +x scripts/backup-postgres-to-s3.sh
```

نمونه سرویس:

```yaml
backup:
  image: python:3.12-alpine
  container_name: letter-mcp-backup
  env_file:
    - .env
  depends_on:
    db:
      condition: service_healthy
  volumes:
    - ./scripts:/scripts:ro
    - backup_tmp:/backup
  command: ["/bin/sh", "/scripts/backup-loop.sh"]
  restart: unless-stopped
```

برای این روش باید `backup-loop.sh` هم داشته باشی که طبق زمان‌بندی اجرا کند.

## روش 2: cron روی host

روی سرور:

```bash
crontab -e
```

اجرای بکاپ روزانه ساعت 03:00:

```cron
0 3 * * * cd /opt/apps/letter-mcp && /bin/bash scripts/backup-postgres-to-s3.sh >> /var/log/letter-mcp-backup.log 2>&1
```

بررسی لاگ:

```bash
tail -f /var/log/letter-mcp-backup.log
```

## تست بکاپ خودکار

قبل از اعتماد به cron، دستی اجرا کن:

```bash
cd /opt/apps/letter-mcp
bash scripts/backup-postgres-to-s3.sh
```

بعد S3 را چک کن:

```bash
set -a
source .env
set +a
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" s3 ls "s3://$BACKUP_S3_BUCKET/$BACKUP_S3_PREFIX/"
```
