#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /backups/file.dump"
  exit 1
fi

: "${DB_HOST:=db}"
: "${DB_PORT:=5432}"
: "${DB_NAME:?DB_NAME is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export PGPASSWORD="$DB_PASSWORD"

pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --clean --if-exists --no-owner "$1"
