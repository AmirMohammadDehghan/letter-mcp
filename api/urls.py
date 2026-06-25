"""Versionless internal API routes consumed by n8n and the Django site."""

from django.urls import path

from .views import (
    GenerateDocumentView,
    GeneratedDocumentDetailView,
    GeneratedDocumentListView,
    MeView,
    TemplateDetailView,
    TemplateListView,
)

app_name = "api"

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("templates/", TemplateListView.as_view(), name="template_list"),
    path("templates/<slug:key>/", TemplateDetailView.as_view(), name="template_detail"),
    path("generate/", GenerateDocumentView.as_view(), name="generate_document"),
    path("documents/", GeneratedDocumentListView.as_view(), name="document_list"),
    path("documents/<int:document_id>/", GeneratedDocumentDetailView.as_view(), name="document_detail"),
]
