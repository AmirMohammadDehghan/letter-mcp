from django.contrib import admin
from django.forms import ModelForm, TextInput
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import NovaAdminTheme


class ColorInput(TextInput):
    input_type = 'color'
    template_name = 'django/forms/widgets/input.html'

    def __init__(self, attrs=None):
        base_attrs = {'class': 'nova-color-input'}
        if attrs:
            base_attrs.update(attrs)
        super().__init__(base_attrs)


class NovaAdminThemeForm(ModelForm):
    class Meta:
        model = NovaAdminTheme
        fields = '__all__'
        color_fields = (
            'primary_color', 'primary_hover_color', 'info_color', 'success_color', 'warning_color', 'danger_color',
            'dark_background', 'dark_surface', 'dark_surface_alt', 'dark_text', 'dark_text_soft', 'dark_muted', 'dark_border',
            'light_background', 'light_surface', 'light_surface_alt', 'light_text', 'light_text_soft', 'light_muted', 'light_border',
        )
        widgets = {field: ColorInput for field in color_fields}


@admin.register(NovaAdminTheme)
class NovaAdminThemeAdmin(admin.ModelAdmin):
    form = NovaAdminThemeForm
    list_display = ('name', 'is_active', 'color_preview', 'theme_mode', 'default_sidebar_state', 'compact_mode', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'theme_mode', 'compact_mode', 'default_sidebar_state')
    search_fields = ('name', 'site_title', 'site_header', 'site_brand')
    readonly_fields = ('live_preview', 'updated_at')
    fieldsets = (
        (_('Identity and branding'), {
            'fields': ('name', 'is_active', 'site_title', 'site_header', 'site_brand', 'brand_logo', 'favicon', 'live_preview'),
        }),
        (_('Core colors'), {
            'fields': ('theme_mode', 'primary_color', 'primary_hover_color', 'info_color', 'success_color', 'warning_color', 'danger_color'),
        }),
        (_('Dark palette'), {
            'classes': ('collapse',),
            'fields': ('dark_background', 'dark_surface', 'dark_surface_alt', 'dark_text', 'dark_text_soft', 'dark_muted', 'dark_border'),
        }),
        (_('Light palette'), {
            'classes': ('collapse',),
            'fields': ('light_background', 'light_surface', 'light_surface_alt', 'light_text', 'light_text_soft', 'light_muted', 'light_border'),
        }),
        (_('Layout'), {
            'fields': ('sidebar_width', 'sidebar_collapsed_width', 'topbar_height', 'border_radius', 'content_spacing_x', 'content_spacing_y', 'font_family', 'compact_mode'),
        }),
        (_('Features'), {
            'fields': ('enable_sidebar_collapse', 'default_sidebar_state', 'show_global_search', 'show_theme_toggle', 'show_dashboard_reports', 'show_recent_actions'),
        }),
        (_('Advanced'), {
            'classes': ('collapse',),
            'fields': ('custom_css', 'updated_at'),
        }),
    )

    class Media:
        css = {'all': ('jazzmin/css/nova-theme-admin.css',)}
        js = ('jazzmin/js/nova-theme-admin.js',)

    @admin.display(description=_('Preview'))
    def color_preview(self, obj):
        return format_html(
            '<span class="nova-admin-palette"><i style="background:{}"></i><i style="background:{}"></i><i style="background:{}"></i><i style="background:{}"></i></span>',
            obj.primary_color, obj.success_color, obj.warning_color, obj.danger_color,
        )

    @admin.display(description=_('Live preview'))
    def live_preview(self, obj=None):
        primary = obj.primary_color if obj else '#2563eb'
        surface = obj.dark_surface if obj else '#111827'
        radius = obj.border_radius if obj else 10
        brand = obj.site_brand or obj.name if obj else 'Nova Admin'
        return format_html(
            '<div class="nova-admin-live-preview" style="--preview-primary:{};--preview-surface:{};--preview-radius:{}px">'
            '<aside><b>{}</b><span></span><span></span><span></span></aside>'
            '<main><header></header><section><i></i><i></i><i></i></section></main>'
            '</div>',
            primary, surface, radius, brand,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_active:
            NovaAdminTheme.objects.exclude(pk=obj.pk).update(is_active=False)
