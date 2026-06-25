# استفاده از API

## احراز هویت

طبق تنظیمات پروژه، APIها به‌صورت پیش‌فرض protected هستند:

```python
DEFAULT_PERMISSION_CLASSES = (
    "rest_framework.permissions.IsAuthenticated",
)
```

و authenticationها:

```python
api.authentication.ServiceAPIKeyAuthentication
rest_framework_simplejwt.authentication.JWTAuthentication
```

## JWT

اگر endpoint دریافت token در `urls.py` فعال باشد، معمولاً مسیرها شبیه این هستند:

```text
/api/token/
/api/token/refresh/
```

نمونه درخواست:

```bash
curl -X POST https://lettermcp.24u.ir/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"PASSWORD"}'
```

استفاده از token:

```bash
curl https://lettermcp.24u.ir/api/SOME_ENDPOINT/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Service API Key برای n8n

اگر پروژه مدل یا admin برای API key دارد، برای n8n بهتر است کاربر/کلید سرویس جدا بسازی.

الگوی header معمولاً باید در `api/authentication.py` بررسی شود. نمونه احتمالی:

```text
X-API-Key: SERVICE_API_KEY
```

یا:

```text
Authorization: Api-Key SERVICE_API_KEY
```

برای اطمینان، فایل زیر را بررسی کن:

```bash
cat api/authentication.py
```

## تست سلامت API

```bash
curl -I https://lettermcp.24u.ir/admin/
curl https://lettermcp.24u.ir/api/
```
