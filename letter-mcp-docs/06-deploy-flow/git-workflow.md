# جریان Git و حل مشکلات pull

## اصل مهم

- کد باید از GitHub بیاید.
- `.env` باید فقط روی سرور باشد و در Git track نشود.
- migrationها باید commit شوند.

## وقتی git pull خطا می‌دهد

خطای نمونه:

```text
error: Your local changes to the following files would be overwritten by merge:
    .env
    core/settings.py
Please commit your changes or stash them before you merge.
```

### راه امن

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

### حذف .env از Git برای همیشه

روی سیستم توسعه:

```bash
echo ".env" >> .gitignore
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking env file"
git push origin main
```

روی سرور:

```bash
cp .env .env.server.backup
git pull origin main
cp .env.server.backup .env
```

## استفاده از SSH روی پورت 443 برای GitHub

اگر پورت 22 مشکل داشت:

```bash
mkdir -p ~/.ssh
nano ~/.ssh/config
```

محتوا:

```text
Host github.com
    Hostname ssh.github.com
    Port 443
    User git
```

تست:

```bash
ssh -T git@github.com
```
