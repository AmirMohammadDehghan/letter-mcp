# Generated manually for service API key support.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0002_accounts_jwt_audit_idempotency"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceAPIKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="نام کلید")),
                ("key_prefix", models.CharField(editable=False, max_length=16, unique=True, verbose_name="پیشوند قابل نمایش", help_text="برای شناسایی کلید در پنل؛ خود کلید واقعی ذخیره نمی‌شود.")),
                ("key_hash", models.CharField(editable=False, max_length=64, verbose_name="هش کلید")),
                ("allowed_sources", models.JSONField(blank=True, default=list, verbose_name="منابع مجاز", help_text='اگر خالی باشد همه منابع مجازند؛ نمونه: ["n8n"]')),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("expires_at", models.DateTimeField(blank=True, null=True, verbose_name="تاریخ انقضا")),
                ("last_used_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین استفاده")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_service_api_keys", to=settings.AUTH_USER_MODEL, verbose_name="سازنده کلید")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="service_api_keys", to=settings.AUTH_USER_MODEL, verbose_name="مالک کلید")),
            ],
            options={
                "verbose_name": "کلید API سرویس",
                "verbose_name_plural": "کلیدهای API سرویس",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="serviceapikey",
            index=models.Index(fields=["owner", "is_active"], name="api_service_owner_i_8ce34d_idx"),
        ),
        migrations.AddIndex(
            model_name="serviceapikey",
            index=models.Index(fields=["key_prefix"], name="api_service_key_pre_7b677e_idx"),
        ),
    ]
