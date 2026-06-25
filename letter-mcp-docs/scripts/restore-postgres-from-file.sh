#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 backups/letter-mcp-postgres-YYYYmmdd-HHMMSS.dump"
  exit 1
fi

BACKUP_FILE="$1"
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "[restore] stopping web"
docker compose stop web

echo "[restore] restoring $BACKUP_FILE to $DB_NAME"
cat "$BACKUP_FILE" | docker compose exec -T db pg_restore \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --clean \
  --if-exists \
  --no-owner

echo "[restore] starting web"
docker compose start web

echo "[restore] running migrations"
docker compose exec web python manage.py migrate

echo "[restore] done"
