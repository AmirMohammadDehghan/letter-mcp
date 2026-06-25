# مستندات کامل دیپلوی و نگهداری پروژه Letter MCP

این پکیج مستندات، مسیر کامل آماده‌سازی، دیپلوی، تنظیمات، نگهداری، بکاپ، restore، توسعه و عیب‌یابی پروژه `letter-mcp` را پوشش می‌دهد.

> نکته امنیتی: در این مستندات هیچ secret واقعی، password، access key یا private key ذخیره نشده است. مقادیر حساس را با placeholder جایگزین کنید و کلیدهایی که در گفتگو یا لاگ‌ها افشا شده‌اند را rotate کنید.

## ساختار مستندات

```text
letter-mcp-docs/
├── 01-overview/
│   ├── architecture.md
│   └── project-structure.md
├── 02-server/
│   ├── server-preparation.md
│   └── firewall-and-domain.md
├── 03-config/
│   ├── env-reference.md
│   ├── production-settings-py.md
│   └── secrets-and-rotation.md
├── 04-docker/
│   ├── docker-compose.md
│   ├── dockerfile-entrypoint.md
│   └── common-commands.md
├── 05-storage-s3-rustfs/
│   ├── buckets.md
│   ├── static-and-media.md
│   ├── cors.md
│   └── rustfs-tests.md
├── 06-deploy-flow/
│   ├── first-deploy.md
│   ├── update-deploy.md
│   ├── git-workflow.md
│   └── migrations-and-static.md
├── 07-backup-restore/
│   ├── backup-strategy.md
│   ├── manual-backup.md
│   ├── automatic-backup.md
│   └── restore.md
├── 08-admin-api/
│   ├── superuser-admin.md
│   └── api-usage.md
├── 09-troubleshooting/
│   ├── static-errors.md
│   ├── allowed-hosts-400.md
│   ├── s3-errors.md
│   ├── docker-errors.md
│   └── git-pull-conflicts.md
├── 10-checklists/
│   ├── deploy-checklist.md
│   ├── after-deploy-checklist.md
│   └── incident-checklist.md
└── scripts/
    ├── backup-postgres-to-s3.sh
    ├── restore-postgres-from-file.sh
    ├── check-django-settings.sh
    └── deploy-update.sh
```

## مسیر پیشنهادی مطالعه

برای بار اول:

1. `01-overview/architecture.md`
2. `02-server/server-preparation.md`
3. `03-config/env-reference.md`
4. `03-config/production-settings-py.md`
5. `05-storage-s3-rustfs/static-and-media.md`
6. `06-deploy-flow/first-deploy.md`
7. `07-backup-restore/backup-strategy.md`
8. `10-checklists/deploy-checklist.md`

برای آپدیت‌های بعدی:

1. `06-deploy-flow/update-deploy.md`
2. `06-deploy-flow/git-workflow.md`
3. `06-deploy-flow/migrations-and-static.md`
4. `10-checklists/after-deploy-checklist.md`

برای خطاها:

- ارور 400: `09-troubleshooting/allowed-hosts-400.md`
- static admin لود نمی‌شود: `09-troubleshooting/static-errors.md`
- مشکل S3/RustFS: `09-troubleshooting/s3-errors.md`
- مشکل Docker/Gunicorn: `09-troubleshooting/docker-errors.md`
- مشکل git pull: `09-troubleshooting/git-pull-conflicts.md`
