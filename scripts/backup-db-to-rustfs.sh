#!/bin/sh
set -e

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${AWS_S3_ENDPOINT_URL:?AWS_S3_ENDPOINT_URL is required}"
: "${BACKUP_S3_BUCKET:?BACKUP_S3_BUCKET is required}"
: "${BACKUP_S3_PREFIX:=letter-mcp/postgres}"
: "${BACKUP_RETENTION_DAYS:=14}"

export PGPASSWORD="$DB_PASSWORD"
export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="${AWS_S3_REGION_NAME:-us-east-1}"

mkdir -p /backups
TS="$(date +%Y%m%d-%H%M%S)"
FILE="/backups/${DB_NAME}-${TS}.dump"
S3_URI="s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}/${DB_NAME}-${TS}.dump"

echo "Creating PostgreSQL backup: $FILE"
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Fc -f "$FILE"

echo "Uploading backup to: $S3_URI"
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" s3 cp "$FILE" "$S3_URI"

echo "Removing local backups older than ${BACKUP_RETENTION_DAYS} days"
find /backups -type f -name "*.dump" -mtime +"$BACKUP_RETENTION_DAYS" -delete

echo "Backup completed: $S3_URI"
