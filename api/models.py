"""Domain models for account-scoped DOCX template generation."""

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
import hashlib
import secrets



def template_upload_to(instance: "DocumentTemplate", filename: str) -> str:
    """Store template files under the owning account for easier auditing."""
    owner_id = instance.owner_id or "unassigned"
    template_key = instance.key or "template"
    return f"templates/user_{owner_id}/{template_key}/{filename}"


def generated_upload_to(instance: "GeneratedDocument", filename: str) -> str:
    """Store generated documents under the account and template that produced them."""
    owner_id = instance.owner_id or "unassigned"
    template_key = getattr(instance.template, "key", "template")
    return f"generated/user_{owner_id}/{template_key}/{filename}"


class ServiceAPIKey(models.Model):
    """
    A long-lived machine credential for n8n or other trusted automation tools.

    Security notes:
    - The raw API key is shown only once by the management command/admin workflow.
    - Only a SHA-256 hash derived from the raw key is stored in the database.
    - The key is scoped to one owner, so all templates/documents remain account-scoped.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_api_keys",
        verbose_name="مالک کلید",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_service_api_keys",
        verbose_name="سازنده کلید",
    )
    name = models.CharField(max_length=120, verbose_name="نام کلید")
    key_prefix = models.CharField(
        max_length=16,
        unique=True,
        editable=False,
        verbose_name="پیشوند قابل نمایش",
        help_text="برای شناسایی کلید در پنل؛ خود کلید واقعی ذخیره نمی‌شود.",
    )
    key_hash = models.CharField(max_length=64, editable=False, verbose_name="هش کلید")
    allowed_sources = models.JSONField(
        default=list,
        blank=True,
        verbose_name="منابع مجاز",
        help_text='اگر خالی باشد همه منابع مجازند؛ نمونه: ["n8n"]',
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ انقضا")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین استفاده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "کلید API سرویس"
        verbose_name_plural = "کلیدهای API سرویس"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "is_active"]),
            models.Index(fields=["key_prefix"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.owner} - {self.key_prefix}"

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at <= timezone.now())

    @property
    def masked_key(self) -> str:
        return f"{self.key_prefix}..."

    @classmethod
    def generate_plain_key(cls) -> str:
        """Generate a human-copyable service key with an identifiable prefix."""
        return f"n8n_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """
        Hash the raw key with Django SECRET_KEY as a server-side pepper.

        If SECRET_KEY changes, existing service keys intentionally become invalid.
        """
        payload = f"{settings.SECRET_KEY}:{raw_key}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @classmethod
    def build(cls, *, owner, name: str, created_by=None, allowed_sources=None, expires_at=None):
        """Create a ServiceAPIKey instance and return it together with the raw key."""
        raw_key = cls.generate_plain_key()
        instance = cls.objects.create(
            owner=owner,
            created_by=created_by,
            name=name,
            key_prefix=raw_key[:12],
            key_hash=cls.hash_key(raw_key),
            allowed_sources=allowed_sources or [],
            expires_at=expires_at,
        )
        return instance, raw_key

    def matches(self, raw_key: str) -> bool:
        return secrets.compare_digest(self.key_hash, self.hash_key(raw_key))

    def mark_used(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])


class DocumentTemplate(models.Model):
    """
    A DOCX template owned by one account/user.

    n8n and other API clients should reference templates by `key`, not by the
    Persian display name. The key can stay stable even if the admin renames the
    template for end users.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_templates",
        verbose_name="مالک قالب",
    )
    name = models.CharField(max_length=150, verbose_name="نام قالب")
    key = models.SlugField(max_length=120, verbose_name="کد یکتای قالب")
    template_file = models.FileField(upload_to=template_upload_to, verbose_name="فایل قالب")
    required_fields = models.JSONField(
        default=list,
        blank=True,
        verbose_name="فیلدهای الزامی",
        help_text='مانند: ["date", "recipient_name", "subject"]',
    )
    sample_variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="نمونه داده",
        help_text="برای راهنمای n8n و تست سریع قالب استفاده می‌شود.",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "قالب نامه"
        verbose_name_plural = "قالب‌های نامه"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "key"],
                name="unique_template_key_per_owner",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "is_active", "key"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.key})"


class GeneratedDocument(models.Model):
    """A generated letter and the audit trail of who created it."""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESS = "success", "موفق"
        FAILED = "failed", "ناموفق"

    class Source(models.TextChoices):
        API = "api", "API"
        N8N = "n8n", "n8n"
        ADMIN = "admin", "ادمین"
        UNKNOWN = "unknown", "نامشخص"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_generated_documents",
        verbose_name="مالک نامه",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_documents",
        verbose_name="سازنده نامه",
    )
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.PROTECT,
        related_name="generated_documents",
        verbose_name="قالب",
    )
    variables = models.JSONField(default=dict, verbose_name="داده‌های ورودی")
    meta = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="اطلاعات جانبی",
        help_text="اطلاعات فلو n8n، execution id، شماره درخواست یا داده‌های رهگیری.",
    )
    idempotency_key = models.CharField(
        max_length=180,
        null=True,
        blank=True,
        verbose_name="کلید جلوگیری از تولید تکراری",
        help_text="برای retry امن در n8n استفاده می‌شود؛ هر کلید در هر حساب فقط یک خروجی دارد.",
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.API,
        verbose_name="منبع ساخت",
    )
    output_file = models.FileField(
        upload_to=generated_upload_to,
        blank=True,
        null=True,
        verbose_name="فایل خروجی",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت",
    )
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "نامه تولیدشده"
        verbose_name_plural = "نامه‌های تولیدشده"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "idempotency_key"],
                condition=Q(idempotency_key__isnull=False),
                name="unique_document_idempotency_per_owner",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "status", "created_at"]),
            models.Index(fields=["created_by", "created_at"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.template.name} - #{self.pk}"

    @property
    def storage_key(self) -> str:
        """Return the object key/path stored in RustFS or local storage."""
        return self.output_file.name if self.output_file else ""
