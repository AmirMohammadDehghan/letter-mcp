"""Serializers for the letter generation API."""

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import DocumentTemplate, GeneratedDocument

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Safe user representation for audit fields."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "full_name"]

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name()


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Template metadata exposed to n8n and the Django site."""

    owner = UserSummarySerializer(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "key",
            "description",
            "required_fields",
            "sample_variables",
            "is_active",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class GenerateDocumentRequestSerializer(serializers.Serializer):
    """Input contract for POST /api/generate/."""

    template_key = serializers.SlugField(max_length=120)
    variables = serializers.DictField(child=serializers.JSONField(), allow_empty=True)
    meta = serializers.DictField(child=serializers.JSONField(), required=False, allow_empty=True)
    idempotency_key = serializers.CharField(
        max_length=180,
        required=False,
        allow_blank=False,
        help_text="Use n8n execution id or a business request id to make retries safe.",
    )
    source = serializers.ChoiceField(
        choices=GeneratedDocument.Source.choices,
        required=False,
        default=GeneratedDocument.Source.API,
    )

    def validate_variables(self, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise serializers.ValidationError("variables must be a JSON object.")
        return value


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    """Generated document payload returned to API clients."""

    template_key = serializers.CharField(source="template.key", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True)
    owner = UserSummarySerializer(read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    storage_key = serializers.CharField(read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocument
        fields = [
            "id",
            "status",
            "source",
            "template_key",
            "template_name",
            "owner",
            "created_by",
            "variables",
            "meta",
            "idempotency_key",
            "storage_key",
            "download_url",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_download_url(self, obj: GeneratedDocument) -> str | None:
        if obj.status != GeneratedDocument.Status.SUCCESS or not obj.output_file:
            return None

        try:
            url = obj.output_file.url
        except Exception:  # noqa: BLE001 - storage errors should not break list APIs.
            return None

        request = self.context.get("request")
        if request and not url.startswith(("http://", "https://")):
            return request.build_absolute_uri(url)
        return url
