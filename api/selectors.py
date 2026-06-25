"""Read-side query helpers.

Keeping query logic here makes API views small and keeps authorization filters
consistent across endpoints.
"""

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import DocumentTemplate, GeneratedDocument

User = get_user_model()


class TemplateSelector:
    """Account-scoped template queries."""

    @staticmethod
    def visible_to(user: User, *, active_only: bool = True) -> QuerySet[DocumentTemplate]:
        qs = DocumentTemplate.objects.select_related("owner").filter(owner=user)
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by("name")

    @staticmethod
    def get_active_for_user(user: User, key: str) -> DocumentTemplate:
        return DocumentTemplate.objects.select_related("owner").get(
            owner=user,
            key=key,
            is_active=True,
        )


class GeneratedDocumentSelector:
    """Document queries with safe default scoping."""

    @staticmethod
    def visible_to(user: User, *, scope: str = "mine") -> QuerySet[GeneratedDocument]:
        # Staff/superusers can inspect all documents for operational support.
        # Normal users always remain scoped to their own account.
        if scope == "all" and user.is_staff:
            qs = GeneratedDocument.objects.all()
        else:
            qs = GeneratedDocument.objects.filter(owner=user)

        return qs.select_related("template", "owner", "created_by").order_by("-created_at")
