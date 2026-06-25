# نسخه production فایل core/settings.py

این نسخه برای معماری زیر آماده شده است:

```text
Django + Gunicorn + PostgreSQL + Arvan CDN + RustFS/S3
media bucket  = my-docgen-bucket
static bucket = static-docgen-bucket
```

فایل مسیر:

```text
/opt/apps/letter-mcp/core/settings.py
```

> اگر این فایل را روی سرور دستی تغییر می‌دهی، همان تغییر را در GitHub هم commit کن تا در pull بعدی از بین نرود.

```python
"""
Django settings for the letter generation service.

Production intent:
- The admin panel is used to manage DOCX templates.
- Authenticated API users, including n8n service accounts, generate letters.
- Media files can be stored locally in development or in RustFS/S3 in production.
- Static files can be stored locally in development or uploaded to a separate RustFS/S3 bucket in production.
"""

from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DEBUG", False)
DEPLOY = env_bool("DEPLOY", False)

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "lettermcp.24u.ir,93.118.112.69,127.0.0.1,localhost",
)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    "https://lettermcp.24u.ir,http://93.118.112.69:8002",
)

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "storages",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

if DEPLOY:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.authentication.ServiceAPIKeyAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "7"))
    ),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

USE_S3_MEDIA = env_bool("USE_S3_MEDIA", False)
USE_S3_STATIC = env_bool("USE_S3_STATIC", False)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "my-docgen-bucket")
AWS_STATIC_BUCKET_NAME = os.getenv("AWS_STATIC_BUCKET_NAME", "static-docgen-bucket")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "https://storage.24u.ir").rstrip("/")
AWS_S3_VERIFY = env_bool("AWS_S3_VERIFY", True)
AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "path")
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
AWS_QUERYSTRING_EXPIRE = int(os.getenv("AWS_QUERYSTRING_EXPIRE", "86400"))
S3_MEDIA_LOCATION = os.getenv("S3_MEDIA_LOCATION", "media").strip()
S3_STATIC_LOCATION = os.getenv("S3_STATIC_LOCATION", "static").strip()
MEDIA_QUERYSTRING_AUTH = env_bool("MEDIA_QUERYSTRING_AUTH", True)
STATIC_QUERYSTRING_AUTH = env_bool("STATIC_QUERYSTRING_AUTH", False)
MEDIA_FILE_OVERWRITE = env_bool("MEDIA_FILE_OVERWRITE", False)
STATIC_FILE_OVERWRITE = env_bool("STATIC_FILE_OVERWRITE", True)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

if USE_S3_MEDIA:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "addressing_style": AWS_S3_ADDRESSING_STYLE,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
            "default_acl": None,
            "querystring_auth": MEDIA_QUERYSTRING_AUTH,
            "querystring_expire": AWS_QUERYSTRING_EXPIRE,
            "file_overwrite": MEDIA_FILE_OVERWRITE,
            "verify": AWS_S3_VERIFY,
            "location": S3_MEDIA_LOCATION,
        },
    }
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{S3_MEDIA_LOCATION}/"

if USE_S3_STATIC:
    STORAGES["staticfiles"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STATIC_BUCKET_NAME,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "addressing_style": AWS_S3_ADDRESSING_STYLE,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
            "default_acl": "public-read",
            "querystring_auth": STATIC_QUERYSTRING_AUTH,
            "file_overwrite": STATIC_FILE_OVERWRITE,
            "verify": AWS_S3_VERIFY,
            "location": S3_STATIC_LOCATION,
        },
    }
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STATIC_BUCKET_NAME}/{S3_STATIC_LOCATION}/"

SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", DEPLOY and not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", DEPLOY and not DEBUG)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
X_FRAME_OPTIONS = "DENY"
```
