#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${AWS_S3_ENDPOINT_URL:?AWS_S3_ENDPOINT_URL is required}"
: "${BACKUP_S3_BUCKET:?BACKUP_S3_BUCKET is required}"

BACKUP_S3_PREFIX="${BACKUP_S3_PREFIX:-postgres}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${BACKUP_DIR:-backups}"
FILE="letter-mcp-postgres-${TS}.dump"

mkdir -p "$BACKUP_DIR"

echo "[backup] dumping PostgreSQL to $BACKUP_DIR/$FILE"
docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$BACKUP_DIR/$FILE"

echo "[backup] uploading to s3://$BACKUP_S3_BUCKET/$BACKUP_S3_PREFIX/$FILE"
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" \
  s3 cp "$BACKUP_DIR/$FILE" "s3://$BACKUP_S3_BUCKET/$BACKUP_S3_PREFIX/$FILE"

echo "[backup] removing local files older than $BACKUP_RETENTION_DAYS days"
find "$BACKUP_DIR" -type f -name 'letter-mcp-postgres-*.dump' -mtime "+$BACKUP_RETENTION_DAYS" -delete

echo "[backup] done"
