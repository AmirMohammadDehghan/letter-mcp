import re

from django.core import validators
from django.db import models
from django.forms.widgets import TextInput

HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class NovaColorInput(TextInput):
    """Small dependency-free color picker used by Nova Admin themes."""

    input_type = "color"
    template_name = "jazzmin/widgets/color.html"

    def __init__(self, attrs=None):
        attrs = {**(attrs or {}), "class": "nova-color-input"}
        super().__init__(attrs=attrs)


class ColorField(models.CharField):
    """A compact django-colorfield style model field without external dependencies."""

    description = "Hex color value"

    default_validators = [
        validators.RegexValidator(
            regex=HEX_COLOR_RE,
            message="Enter a valid HEX color like #0f172a or #2563eb.",
        )
    ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault("widget", NovaColorInput)
        return super().formfield(**kwargs)
