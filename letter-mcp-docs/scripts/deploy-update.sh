#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[deploy] pulling latest code"
git pull origin main

echo "[deploy] rebuilding containers"
docker compose up -d --build

echo "[deploy] running migrations"
docker compose exec web python manage.py migrate

echo "[deploy] collecting static"
docker compose exec web python manage.py collectstatic --noinput --clear -v 2

echo "[deploy] restarting web"
docker compose restart web

echo "[deploy] status"
docker compose ps

echo "[deploy] done"
