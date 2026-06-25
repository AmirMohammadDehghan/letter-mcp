# CORS برای static bucket و فونت‌ها

## چرا نیاز است؟

وقتی سایت روی این دامنه است:

```text
https://lettermcp.24u.ir
```

ولی فونت‌ها از این دامنه لود می‌شوند:

```text
https://storage.24u.ir/static-docgen-bucket/...
```

مرورگر برای فایل‌های font مثل `.woff2` هدر CORS می‌خواهد.

## خطای نمونه

```text
Cross-Origin Request Blocked
Reason: CORS header 'Access-Control-Allow-Origin' missing
```

## CORS پیشنهادی برای static bucket

اگر پنل RustFS JSON لیستی می‌خواهد:

```json
[
  {
    "AllowedOrigins": [
      "https://lettermcp.24u.ir",
      "https://www.lettermcp.24u.ir"
    ],
    "AllowedMethods": [
      "GET",
      "HEAD"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "ETag",
      "Content-Length",
      "Content-Type"
    ],
    "MaxAgeSeconds": 3000
  }
]
```

برای AWS CLI فرمت باید داخل `CORSRules` باشد:

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": [
        "https://lettermcp.24u.ir",
        "https://www.lettermcp.24u.ir"
      ],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

اعمال با AWS CLI:

```bash
aws --endpoint-url "$AWS_S3_ENDPOINT_URL" \
  s3api put-bucket-cors \
  --bucket "$AWS_STATIC_BUCKET_NAME" \
  --cors-configuration file://cors-static.json
```

## تست واقعی CORS

```bash
curl -I \
  -H "Origin: https://lettermcp.24u.ir" \
  https://storage.24u.ir/static-docgen-bucket/static/jazzmin/fonts/vazirmatn/Vazirmatn-Regular.woff2
```

باید یکی از این‌ها را ببینی:

```text
access-control-allow-origin: https://lettermcp.24u.ir
```

یا:

```text
access-control-allow-origin: *
```

اگر فایل `200` است ولی هدر CORS ندارد، مشکل از CORS bucket یا cache CDN روی `storage.24u.ir` است.

## پاک کردن cache

در Arvan دامنه `storage.24u.ir`:

```text
CDN -> Cache -> Purge Cache
```

مسیر پیشنهادی:

```text
/static-docgen-bucket/static/*
```
