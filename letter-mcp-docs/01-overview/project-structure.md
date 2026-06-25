# ساختار پروژه

نمونه ساختار اصلی روی سرور:

```text
/opt/apps/letter-mcp/
├── Dockerfile
├── README.md
├── README-DEPLOY.md
├── api/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── docker-compose.yml
├── entrypoint.sh
├── manage.py
├── media/
├── requirements.txt
├── scripts/
└── staticfiles/
```

## مسیرهای مهم

| مسیر | توضیح |
|---|---|
| `core/settings.py` | تنظیمات اصلی Django، دیتابیس، S3، static و media |
| `.env` | تنظیمات محرمانه و production روی سرور. نباید در Git commit شود. |
| `docker-compose.yml` | تعریف سرویس‌های web، db، backup |
| `Dockerfile` | ساخت image اپلیکیشن |
| `entrypoint.sh` | اجرای migrate، collectstatic و سپس Gunicorn |
| `api/` | کدهای API، مدل‌ها، احراز هویت service API key |
| `staticfiles/` | مقصد local collectstatic در حالت local/WhiteNoise |
| `media/` | فایل‌های media در حالت local |

## فایل‌هایی که نباید در Git باشند

```gitignore
.env
.env.*
!.env.example
media/
staticfiles/
db.sqlite3
*.sqlite3
__pycache__/
*.pyc
```

## اصل مهم

- کد پروژه باید از GitHub بیاید.
- `.env` مخصوص سرور است و باید روی سرور نگهداری شود.
- اگر روی سرور دستی `settings.py` را تغییر دادی، حتماً بعداً همان تغییر را به GitHub منتقل کن تا در pull بعدی از بین نرود.
