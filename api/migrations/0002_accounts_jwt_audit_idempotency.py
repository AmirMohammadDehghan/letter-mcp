# Generated manually for account-scoped templates, JWT API audit trail and idempotency.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q
from django.utils.text import slugify

import api.models


def populate_owner_key_and_audit_fields(apps, schema_editor):
    User = apps.get_model("auth", "User")
    DocumentTemplate = apps.get_model("api", "DocumentTemplate")
    GeneratedDocument = apps.get_model("api", "GeneratedDocument")

    user = User.objects.order_by("id").first()
    if user is None:
        user = User.objects.create(
            username="system",
            is_active=False,
            is_staff=True,
            is_superuser=True,
            password="!",
        )

    seen_keys = set()
    for template in DocumentTemplate.objects.order_by("id"):
        if not template.owner_id:
            template.owner = user

        base_key = slugify(template.name) or f"template-{template.pk}"
        key = template.key or base_key
        suffix = 2
        while (template.owner_id, key) in seen_keys or DocumentTemplate.objects.filter(
            owner_id=template.owner_id,
            key=key,
        ).exclude(pk=template.pk).exists():
            key = f"{base_key}-{suffix}"
            suffix += 1

        template.key = key
        template.save(update_fields=["owner", "key"])
        seen_keys.add((template.owner_id, template.key))

    for document in GeneratedDocument.objects.select_related("template").order_by("id"):
        owner = document.template.owner if document.template_id else user
        changed_fields = []
        if not document.owner_id:
            document.owner = owner
            changed_fields.append("owner")
        if not document.created_by_id:
            document.created_by = owner
            changed_fields.append("created_by")
        if not document.status:
            document.status = "success" if document.output_file else "pending"
            changed_fields.append("status")
        if changed_fields:
            document.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="documenttemplate",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_templates",
                to=settings.AUTH_USER_MODEL,
                verbose_name="مالک قالب",
            ),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="key",
            field=models.SlugField(blank=True, max_length=120, null=True, verbose_name="کد یکتای قالب"),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="sample_variables",
            field=models.JSONField(blank=True, default=dict, verbose_name="نمونه داده"),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="description",
            field=models.TextField(blank=True, verbose_name="توضیحات"),
        ),
        migrations.AddField(
            model_name="documenttemplate",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی"),
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="name",
            field=models.CharField(max_length=150, verbose_name="نام قالب"),
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="template_file",
            field=models.FileField(upload_to=api.models.template_upload_to, verbose_name="فایل قالب"),
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="required_fields",
            field=models.JSONField(blank=True, default=list, verbose_name="فیلدهای الزامی"),
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="فعال"),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_generated_documents",
                to=settings.AUTH_USER_MODEL,
                verbose_name="مالک نامه",
            ),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="generated_documents",
                to=settings.AUTH_USER_MODEL,
                verbose_name="سازنده نامه",
            ),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="meta",
            field=models.JSONField(blank=True, default=dict, verbose_name="اطلاعات جانبی"),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="idempotency_key",
            field=models.CharField(blank=True, max_length=180, null=True, verbose_name="کلید جلوگیری از تولید تکراری"),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="source",
            field=models.CharField(
                choices=[("api", "API"), ("n8n", "n8n"), ("admin", "ادمین"), ("unknown", "نامشخص")],
                default="api",
                max_length=20,
                verbose_name="منبع ساخت",
            ),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="status",
            field=models.CharField(
                choices=[("pending", "در انتظار"), ("success", "موفق"), ("failed", "ناموفق")],
                default="pending",
                max_length=20,
                verbose_name="وضعیت",
            ),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="error_message",
            field=models.TextField(blank=True, verbose_name="پیام خطا"),
        ),
        migrations.AddField(
            model_name="generateddocument",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی"),
        ),
        migrations.AlterField(
            model_name="generateddocument",
            name="output_file",
            field=models.FileField(blank=True, null=True, upload_to=api.models.generated_upload_to, verbose_name="فایل خروجی"),
        ),
        migrations.RunPython(populate_owner_key_and_audit_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="documenttemplate",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="document_templates",
                to=settings.AUTH_USER_MODEL,
                verbose_name="مالک قالب",
            ),
        ),
        migrations.AlterField(
            model_name="documenttemplate",
            name="key",
            field=models.SlugField(max_length=120, verbose_name="کد یکتای قالب"),
        ),
        migrations.AlterField(
            model_name="generateddocument",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_generated_documents",
                to=settings.AUTH_USER_MODEL,
                verbose_name="مالک نامه",
            ),
        ),
        migrations.AddConstraint(
            model_name="documenttemplate",
            constraint=models.UniqueConstraint(fields=("owner", "key"), name="unique_template_key_per_owner"),
        ),
        migrations.AddConstraint(
            model_name="generateddocument",
            constraint=models.UniqueConstraint(
                fields=("owner", "idempotency_key"),
                condition=Q(idempotency_key__isnull=False),
                name="unique_document_idempotency_per_owner",
            ),
        ),
        migrations.AddIndex(
            model_name="documenttemplate",
            index=models.Index(fields=["owner", "is_active", "key"], name="api_documen_owner_i_5b4a3a_idx"),
        ),
        migrations.AddIndex(
            model_name="generateddocument",
            index=models.Index(fields=["owner", "status", "created_at"], name="api_generat_owner_s_d1a8b2_idx"),
        ),
        migrations.AddIndex(
            model_name="generateddocument",
            index=models.Index(fields=["created_by", "created_at"], name="api_generat_created_e3d53c_idx"),
        ),
        migrations.AddIndex(
            model_name="generateddocument",
            index=models.Index(fields=["idempotency_key"], name="api_generat_idempot_7199d4_idx"),
        ),
    ]
