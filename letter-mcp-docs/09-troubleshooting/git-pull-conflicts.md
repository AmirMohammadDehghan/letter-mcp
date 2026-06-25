# حل conflict و مشکل git pull روی سرور

## خطای رایج

```text
error: Your local changes to the following files would be overwritten by merge:
    .env
    core/settings.py
Please commit your changes or stash them before you merge.
```

## راه امن

```bash
cd /opt/apps/letter-mcp
cp .env .env.server.backup
cp core/settings.py core/settings.py.server.backup

git stash push -m "server local changes before pull" -- .env core/settings.py
git pull origin main
cp .env.server.backup .env
```

بعد:

```bash
docker compose build --no-cache web
docker compose up -d
```

## اگر فقط settings.py را می‌خواهی از Git بگیری

```bash
cp .env .env.server.backup
git checkout -- core/settings.py
git pull origin main
cp .env.server.backup .env
```

اگر `.env` هم conflict داد:

```bash
git checkout -- .env
git pull origin main
cp .env.server.backup .env
```

## راه دائمی

`.env` را از Git خارج کن:

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking env file"
git push origin main
```
