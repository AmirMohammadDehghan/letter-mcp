"""Business services for generating DOCX letters.

The service layer intentionally owns validation, idempotency, rendering and
status transitions. Views only parse HTTP input and serialize output.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import os
import tempfile
from typing import Any
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.utils.text import slugify
from docxtpl import DocxTemplate

from .models import DocumentTemplate, GeneratedDocument
from .selectors import TemplateSelector

User = get_user_model()


class DocumentGenerationError(Exception):
    """Base exception for controlled document generation failures."""


class MissingTemplateFieldsError(DocumentGenerationError):
    """Raised when input variables do not include all required template fields."""

    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(f"Missing required fields: {missing_fields}")


@dataclass(frozen=True)
class GenerationResult:
    """Service result returned to API views."""

    document: GeneratedDocument
    reused: bool = False


class DocxTemplateRenderer:
    """Render a DOCX template from any Django storage backend.

    docxtpl needs a local filesystem path. RustFS/S3 storage does not provide a
    local path, so we stream the template into a temporary file and always clean
    it up in a finally block.
    """

    def render(self, template: DocumentTemplate, variables: dict[str, Any]) -> bytes:
        tmp_path: str | None = None
        try:
            with template.template_file.open("rb") as template_file:
                template_bytes = template_file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                tmp_file.write(template_bytes)
                tmp_path = tmp_file.name

            doc = DocxTemplate(tmp_path)
            doc.render(variables)

            output = BytesIO()
            doc.save(output)
            output.seek(0)
            return output.read()
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


class DocumentGeneratorService:
    """Create letters from account-owned templates with idempotency support."""

    def __init__(self, renderer: DocxTemplateRenderer | None = None):
        self.renderer = renderer or DocxTemplateRenderer()

    def generate(
        self,
        *,
        user: User,
        template_key: str,
        variables: dict[str, Any],
        meta: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        source: str = GeneratedDocument.Source.API,
    ) -> GenerationResult:
        template = TemplateSelector.get_active_for_user(user, template_key)
        normalized_idempotency_key = self._normalize_idempotency_key(
            idempotency_key or (meta or {}).get("request_id")
        )

        if normalized_idempotency_key:
            existing = GeneratedDocument.objects.filter(
                owner=user,
                idempotency_key=normalized_idempotency_key,
            ).select_related("template", "owner", "created_by").first()
            if existing:
                return GenerationResult(document=existing, reused=True)

        self._validate_required_fields(template, variables)

        try:
            with transaction.atomic():
                document = GeneratedDocument.objects.create(
                    owner=user,
                    created_by=user,
                    template=template,
                    variables=variables,
                    meta=meta or {},
                    idempotency_key=normalized_idempotency_key,
                    source=source,
                    status=GeneratedDocument.Status.PENDING,
                )
        except IntegrityError:
            # A concurrent retry with the same idempotency key won the race.
            existing = GeneratedDocument.objects.get(
                owner=user,
                idempotency_key=normalized_idempotency_key,
            )
            return GenerationResult(document=existing, reused=True)

        try:
            rendered_bytes = self.renderer.render(template, variables)
            filename = self._build_output_filename(template, document)
            document.output_file.save(filename, ContentFile(rendered_bytes), save=False)
            document.status = GeneratedDocument.Status.SUCCESS
            document.error_message = ""
            document.save(update_fields=["output_file", "status", "error_message", "updated_at"])
            return GenerationResult(document=document, reused=False)
        except Exception as exc:  # noqa: BLE001 - stored for audit and re-raised safely.
            document.status = GeneratedDocument.Status.FAILED
            document.error_message = str(exc)
            document.save(update_fields=["status", "error_message", "updated_at"])
            raise DocumentGenerationError(str(exc)) from exc

    @staticmethod
    def _validate_required_fields(template: DocumentTemplate, variables: dict[str, Any]) -> None:
        missing = [
            field
            for field in (template.required_fields or [])
            if field not in variables or variables[field] in (None, "")
        ]
        if missing:
            raise MissingTemplateFieldsError(missing)

    @staticmethod
    def _normalize_idempotency_key(value: Any) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _build_output_filename(template: DocumentTemplate, document: GeneratedDocument) -> str:
        template_key = slugify(template.key) or "letter"
        return f"{template_key}-{document.pk}-{uuid4().hex[:10]}.docx"
