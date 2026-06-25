# چک‌لیست دیپلوی اولیه

## قبل از deploy

- [ ] Docker و Docker Compose نصب شده است.
- [ ] پروژه در `/opt/apps/letter-mcp` clone شده است.
- [ ] `.env` ساخته شده و مقدارهای production دارد.
- [ ] `.env` در Git track نمی‌شود.
- [ ] bucketهای S3/RustFS ساخته شده‌اند.
- [ ] CORS روی static bucket تنظیم شده است.
- [ ] دامنه `lettermcp.24u.ir` در Arvan به IP سرور اشاره می‌کند.
- [ ] origin port در Arvan روی `8002` تنظیم شده است.
- [ ] پورت `8002/tcp` در firewall باز است.

## حین deploy

- [ ] `docker compose up -d --build` اجرا شد.
- [ ] `docker compose ps` سرویس web و db را healthy/up نشان می‌دهد.
- [ ] migrate اجرا شد.
- [ ] collectstatic اجرا شد.
- [ ] superuser ساخته شد.

## تست‌های نهایی

```bash
curl -I http://127.0.0.1:8002/admin/
curl -I http://SERVER_IP:8002/admin/ -H "Host: lettermcp.24u.ir"
curl -I https://lettermcp.24u.ir/admin/
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

- [ ] `/admin/` پاسخ `302` می‌دهد.
- [ ] فایل CSS پاسخ `200` و `text/css` می‌دهد.
- [ ] فونت‌ها CORS error ندارند.
- [ ] login admin کار می‌کند.
- [ ] backup دستی تست شده است.
