# تست‌های RustFS/S3

## تست با curl

Static:

```bash
curl -I https://storage.24u.ir/static-docgen-bucket/static/admin/css/base.css
```

Font با CORS:

```bash
curl -I \
  -H "Origin: https://lettermcp.24u.ir" \
  https://storage.24u.ir/static-docgen-bucket/static/jazzmin/fonts/vazirmatn/Vazirmatn-Regular.woff2
```

Media نمونه:

```bash
curl -I https://storage.24u.ir/my-docgen-bucket/media/
```

## تست با mc

```bash
mc alias set rustfs https://storage.24u.ir ACCESS_KEY SECRET_KEY
mc ls rustfs/static-docgen-bucket/static/admin/css/
mc ls rustfs/my-docgen-bucket/media/
```

## تست با awscli

```bash
set -a
source .env
set +a

aws --endpoint-url "$AWS_S3_ENDPOINT_URL" s3 ls "s3://$AWS_STATIC_BUCKET_NAME/static/admin/css/"
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" s3 ls "s3://$AWS_STORAGE_BUCKET_NAME/media/"
```

## خطاهای رایج

| خطا | علت احتمالی |
|---|---|
| 404 | فایل روی bucket نیست یا prefix اشتباه است. |
| 403 | دسترسی public/signed URL درست نیست. |
| CORS missing | CORS روی bucket یا cache CDN مشکل دارد. |
| text/html به جای text/css | فایل static از Django/Arvan HTML برمی‌گرداند، نه S3. |
