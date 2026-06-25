"""Compatibility wrapper for legacy imports.

The production implementation lives in `api.services`. Keeping this wrapper
prevents older integrations from importing a stale generator implementation.
"""

from api.services import (  # noqa: F401
    DocumentGenerationError,
    DocumentGeneratorService,
    DocxTemplateRenderer,
    GenerationResult,
    MissingTemplateFieldsError,
)
