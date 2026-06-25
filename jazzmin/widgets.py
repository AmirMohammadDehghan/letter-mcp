from django.forms.widgets import Select, SelectMultiple


class JazzminSelect(Select):
    """Native select widget kept for backward compatibility."""
    template_name = "jazzmin/widgets/select.html"


class JazzminSelectMultiple(SelectMultiple):
    """Native multiple select widget kept for backward compatibility."""
    template_name = "jazzmin/widgets/select.html"
