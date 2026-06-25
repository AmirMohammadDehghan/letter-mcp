#!/bin/sh
set -e

apk add --no-cache postgresql16-client aws-cli dcron tzdata >/dev/null
chmod +x /scripts/backup-db-to-rustfs.sh /scripts/restore-db-from-file.sh

CRON_EXPR="${BACKUP_CRON:-0 3 * * *}"
echo "$CRON_EXPR /scripts/backup-db-to-rustfs.sh >> /proc/1/fd/1 2>> /proc/1/fd/2" > /etc/crontabs/root

echo "Backup scheduler started. Cron: $CRON_EXPR"
crond -f -l 8
