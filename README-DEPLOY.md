# letter-mcp deploy kit

This kit is designed for the current project structure where `manage.py`, `requirements.txt`, `Dockerfile`, and `entrypoint.sh` live in the repository root.

## First-time server deployment

```bash
cd /opt/apps
git clone https://github.com/AmirMohammadDehghan/letter-mcp.git
cd letter-mcp
cp .env.example .env
nano .env
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

## Nginx

Copy `nginx.conf` to `/etc/nginx/sites-available/lettermcp`, enable it, and reload nginx.

```bash
sudo cp nginx.conf /etc/nginx/sites-available/lettermcp
sudo ln -sf /etc/nginx/sites-available/lettermcp /etc/nginx/sites-enabled/lettermcp
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## Update from GitHub

```bash
cd /opt/apps/letter-mcp
git pull origin main
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose restart web
```

## Manual backup

```bash
docker compose exec backup /scripts/backup-db-to-rustfs.sh
```

## Restore

```bash
docker compose exec backup /scripts/restore-db-from-file.sh /backups/example.dump
```
