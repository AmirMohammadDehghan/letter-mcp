#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose exec web python manage.py shell -c "
from django.conf import settings
from django.core.files.storage import storages
import os
print('DEBUG =', settings.DEBUG)
print('DEPLOY =', settings.DEPLOY)
print('ALLOWED_HOSTS =', settings.ALLOWED_HOSTS)
print('CSRF_TRUSTED_ORIGINS =', settings.CSRF_TRUSTED_ORIGINS)
print('USE_S3_MEDIA env =', os.getenv('USE_S3_MEDIA'))
print('USE_S3_MEDIA settings =', getattr(settings, 'USE_S3_MEDIA', None))
print('USE_S3_STATIC env =', os.getenv('USE_S3_STATIC'))
print('USE_S3_STATIC settings =', getattr(settings, 'USE_S3_STATIC', None))
print('STATIC_URL =', settings.STATIC_URL)
print('MEDIA_URL =', settings.MEDIA_URL)
print('AWS_STATIC_BUCKET_NAME =', getattr(settings, 'AWS_STATIC_BUCKET_NAME', None))
print('AWS_STORAGE_BUCKET_NAME =', getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))
print('staticfiles storage class =', storages['staticfiles'].__class__)
print('default storage class =', storages['default'].__class__)
"
