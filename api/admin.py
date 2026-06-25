"""Admin configuration for templates and generated document audit trail."""

from django.contrib import admin, messages
from django.utils.html import format_html

from .models import DocumentTemplate, GeneratedDocument, ServiceAPIKey


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "owner", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "owner", "created_at")
    search_fields = ("name", "key", "owner__username", "description")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("owner",)
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("owner", "name", "key", "template_file", "is_active")}),
        ("قرارداد داده", {"fields": ("required_fields", "sample_variables")}),
        ("توضیحات", {"fields": ("description",)}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("owner")
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        # Non-superusers can only create templates for themselves.
        if not request.user.is_superuser:
            obj.owner = request.user
        elif not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(ServiceAPIKey)
class ServiceAPIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "key_prefix",
        "is_active",
        "expires_at",
        "last_used_at",
        "created_at",
    )
    list_filter = ("is_active", "owner", "created_at", "last_used_at")
    search_fields = ("name", "owner__username", "key_prefix")
    autocomplete_fields = ("owner", "created_by")
    readonly_fields = (
        "key_prefix",
        "key_hash",
        "last_used_at",
        "created_at",
        "updated_at",
        "security_notice",
    )
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("owner", "created_by", "name", "is_active")}),
        ("محدودیت‌ها", {"fields": ("allowed_sources", "expires_at")}),
        ("اطلاعات امنیتی", {"fields": ("key_prefix", "key_hash", "security_notice")}),
        ("زمان‌ها", {"fields": ("last_used_at", "created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("owner", "created_by")
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        """Generate and show the raw key exactly once when created from Admin.

        The raw value is never saved in the database. Only its hash and a short
        prefix are stored. If the admin misses copying the key from the success
        message, the safe recovery path is to revoke this record and create a
        new key.
        """
        if not obj.created_by_id:
            obj.created_by = request.user

        if not request.user.is_superuser:
            obj.owner = request.user
        elif not obj.owner_id:
            obj.owner = request.user

        if not change:
            raw_key = ServiceAPIKey.generate_plain_key()
            obj.key_prefix = raw_key[:12]
            obj.key_hash = ServiceAPIKey.hash_key(raw_key)
            super().save_model(request, obj, form, change)
            messages.success(
                request,
                format_html(
                    "کلید API ساخته شد. این مقدار فقط همین یک بار نمایش داده می‌شود؛ همین حالا کپی کن: "
                    "<br><code style='direction:ltr; unicode-bidi:embed; font-size:14px; padding:8px; display:inline-block;'>"
                    "{}</code>",
                    raw_key,
                ),
            )
            return

        super().save_model(request, obj, form, change)

    @admin.display(description="راهنمای امنیتی")
    def security_notice(self, obj):
        return format_html(
            "کلید خام در دیتابیس ذخیره نمی‌شود و فقط هنگام ساخت نمایش داده می‌شود. "
            "اگر آن را گم کردی، همین رکورد را غیرفعال کن و یک کلید جدید بساز."
        )


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template",
        "owner",
        "created_by",
        "source",
        "status",
        "idempotency_key",
        "created_at",
        "download_link",
    )
    list_filter = ("status", "source", "owner", "created_by", "created_at")
    search_fields = (
        "template__name",
        "template__key",
        "owner__username",
        "created_by__username",
        "idempotency_key",
    )
    readonly_fields = (
        "owner",
        "created_by",
        "template",
        "variables",
        "meta",
        "idempotency_key",
        "source",
        "output_file",
        "status",
        "error_message",
        "created_at",
        "updated_at",
        "download_link",
    )
    fieldsets = (
        ("اطلاعات نامه", {"fields": ("template", "owner", "created_by", "source", "status")}),
        ("خروجی", {"fields": ("output_file", "download_link", "error_message")}),
        ("داده‌ها", {"fields": ("variables", "meta", "idempotency_key")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        # Generated documents must be produced through the service/API so the
        # audit trail and status transitions remain consistent.
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("template", "owner", "created_by")
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    @admin.display(description="لینک دانلود")
    def download_link(self, obj: GeneratedDocument):
        if obj.status != GeneratedDocument.Status.SUCCESS or not obj.output_file:
            return "-"
        try:
            return format_html('<a href="{}" target="_blank">دانلود</a>', obj.output_file.url)
        except Exception:  # noqa: BLE001
            return "خطا در ساخت لینک"