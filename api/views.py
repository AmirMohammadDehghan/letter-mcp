"""HTTP API views for JWT-protected letter generation."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DocumentTemplate, GeneratedDocument, ServiceAPIKey
from .selectors import GeneratedDocumentSelector, TemplateSelector
from .serializers import (
    DocumentTemplateSerializer,
    GenerateDocumentRequestSerializer,
    GeneratedDocumentSerializer,
    UserSummarySerializer,
)
from .services import (
    DocumentGenerationError,
    DocumentGeneratorService,
    MissingTemplateFieldsError,
)


class MeView(APIView):
    """Return current JWT user details for n8n connection tests."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"status": "success", "user": UserSummarySerializer(request.user).data})


class TemplateListView(APIView):
    """List active templates owned by the authenticated account."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = TemplateSelector.visible_to(request.user, active_only=True)
        serializer = DocumentTemplateSerializer(qs, many=True, context={"request": request})
        return Response({"status": "success", "templates": serializer.data})


class TemplateDetailView(APIView):
    """Return one active template by key, scoped to the authenticated account."""

    permission_classes = [IsAuthenticated]

    def get(self, request, key: str):
        template = get_object_or_404(
            DocumentTemplate.objects.select_related("owner"),
            owner=request.user,
            key=key,
            is_active=True,
        )
        serializer = DocumentTemplateSerializer(template, context={"request": request})
        return Response({"status": "success", "template": serializer.data})


class GenerateDocumentView(APIView):
    """Generate a DOCX letter from one of the user's templates.

    n8n should send an idempotency_key, preferably the execution id or a business
    request id. Repeating the same key returns the existing document instead of
    generating a duplicate file.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateDocumentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        source = data.get("source") or GeneratedDocument.Source.API
        if isinstance(request.auth, ServiceAPIKey):
            allowed_sources = request.auth.allowed_sources or []
            if allowed_sources and source not in allowed_sources:
                return Response(
                    {
                        "status": "error",
                        "error": "source_not_allowed_for_api_key",
                        "allowed_sources": allowed_sources,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        try:
            result = DocumentGeneratorService().generate(
                user=request.user,
                template_key=data["template_key"],
                variables=data["variables"],
                meta=data.get("meta") or {},
                idempotency_key=data.get("idempotency_key"),
                source=source,
            )
        except DocumentTemplate.DoesNotExist:
            return Response(
                {"status": "error", "error": "template not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except MissingTemplateFieldsError as exc:
            return Response(
                {
                    "status": "error",
                    "error": "missing_required_fields",
                    "missing_fields": exc.missing_fields,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DocumentGenerationError as exc:
            return Response(
                {"status": "error", "error": "generation_failed", "detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        output = GeneratedDocumentSerializer(result.document, context={"request": request})
        return Response(
            {"status": "success", "reused": result.reused, "document": output.data},
            status=status.HTTP_200_OK if result.reused else status.HTTP_201_CREATED,
        )


class GeneratedDocumentListView(APIView):
    """List generated letters.

    Normal users see their own account documents. Staff users can add
    ?scope=all for operational visibility across accounts.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        scope = request.query_params.get("scope", "mine")
        qs = GeneratedDocumentSelector.visible_to(request.user, scope=scope)

        template_key = request.query_params.get("template_key")
        status_filter = request.query_params.get("status")
        idempotency_key = request.query_params.get("idempotency_key")

        if template_key:
            qs = qs.filter(template__key=template_key)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if idempotency_key:
            qs = qs.filter(idempotency_key=idempotency_key)

        serializer = GeneratedDocumentSerializer(qs[:100], many=True, context={"request": request})
        return Response({"status": "success", "documents": serializer.data})


class GeneratedDocumentDetailView(APIView):
    """Retrieve a generated document and its current download URL."""

    permission_classes = [IsAuthenticated]

    def get(self, request, document_id: int):
        qs = GeneratedDocumentSelector.visible_to(request.user, scope="mine")
        if request.user.is_staff and request.query_params.get("scope") == "all":
            qs = GeneratedDocumentSelector.visible_to(request.user, scope="all")
        document = get_object_or_404(qs, pk=document_id)
        serializer = GeneratedDocumentSerializer(document, context={"request": request})
        return Response({"status": "success", "document": serializer.data})
