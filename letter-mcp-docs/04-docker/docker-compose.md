# Docker Compose

## سرویس‌های اصلی

پیشنهاد برای `docker-compose.yml`:

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: letter-mcp-web
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8002:8000"
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    container_name: letter-mcp-db
    env_file:
      - .env
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

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

volumes:
  postgres_data:
  backup_tmp:
```

## نکته درباره پورت

اگر می‌خواهی Arvan به origin مستقیم وصل شود:

```yaml
ports:
  - "8002:8000"
```

اگر پشت Nginx داخلی باشد:

```yaml
ports:
  - "127.0.0.1:8002:8000"
```

در پروژه فعلی، چون Arvan مستقیم به 8002 وصل می‌شود، حالت اول لازم است.

## دستورات مهم

بالا آوردن:

```bash
docker compose up -d --build
```

rebuild بدون cache:

```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

دیدن وضعیت:

```bash
docker compose ps
```

لاگ web:

```bash
docker compose logs -f web
```

ورود به shell کانتینر:

```bash
docker compose exec web sh
```

اجرای manage.py:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput --clear -v 2
```
