from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


hex_color_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message=_('Enter a valid hex color like #2563eb.'),
)


class NovaAdminTheme(models.Model):
    THEME_MODE_SYSTEM = 'system'
    THEME_MODE_DARK = 'dark'
    THEME_MODE_LIGHT = 'light'
    THEME_MODE_CHOICES = (
        (THEME_MODE_SYSTEM, _('Follow system preference')),
        (THEME_MODE_DARK, _('Dark')),
        (THEME_MODE_LIGHT, _('Light')),
    )

    SIDEBAR_EXPANDED = 'expanded'
    SIDEBAR_COLLAPSED = 'collapsed'
    SIDEBAR_STATE_CHOICES = (
        (SIDEBAR_EXPANDED, _('Expanded')),
        (SIDEBAR_COLLAPSED, _('Collapsed')),
    )

    name = models.CharField(_('theme name'), max_length=80, default='Default')
    is_active = models.BooleanField(_('active'), default=True)

    site_title = models.CharField(_('site title'), max_length=120, blank=True)
    site_header = models.CharField(_('site header'), max_length=120, blank=True)
    site_brand = models.CharField(_('site brand'), max_length=80, blank=True)
    brand_logo = models.CharField(
        _('brand logo static path'),
        max_length=180,
        blank=True,
        help_text=_('Optional static path, e.g. img/admin-logo.svg or jazzmin/img/default-log.svg.'),
    )
    favicon = models.CharField(
        _('favicon static path'),
        max_length=180,
        blank=True,
        help_text=_('Optional static path for favicon. Leave empty to use the logo.'),
    )

    theme_mode = models.CharField(_('default theme mode'), max_length=12, choices=THEME_MODE_CHOICES, default=THEME_MODE_SYSTEM)
    primary_color = models.CharField(_('primary color'), max_length=7, default='#2563eb', validators=[hex_color_validator])
    primary_hover_color = models.CharField(_('primary hover color'), max_length=7, default='#1d4ed8', validators=[hex_color_validator])
    info_color = models.CharField(_('info color'), max_length=7, default='#0891b2', validators=[hex_color_validator])
    success_color = models.CharField(_('success color'), max_length=7, default='#16a34a', validators=[hex_color_validator])
    warning_color = models.CharField(_('warning color'), max_length=7, default='#d97706', validators=[hex_color_validator])
    danger_color = models.CharField(_('danger color'), max_length=7, default='#dc2626', validators=[hex_color_validator])

    dark_background = models.CharField(_('dark background'), max_length=7, default='#0b1220', validators=[hex_color_validator])
    dark_surface = models.CharField(_('dark surface'), max_length=7, default='#111827', validators=[hex_color_validator])
    dark_surface_alt = models.CharField(_('dark surface alternate'), max_length=7, default='#1e293b', validators=[hex_color_validator])
    dark_text = models.CharField(_('dark text'), max_length=7, default='#e5e7eb', validators=[hex_color_validator])
    dark_text_soft = models.CharField(_('dark secondary text'), max_length=7, default='#b6c2d1', validators=[hex_color_validator])
    dark_muted = models.CharField(_('dark muted text'), max_length=7, default='#8a98aa', validators=[hex_color_validator])
    dark_border = models.CharField(_('dark border'), max_length=7, default='#334155', validators=[hex_color_validator])

    light_background = models.CharField(_('light background'), max_length=7, default='#f4f7fb', validators=[hex_color_validator])
    light_surface = models.CharField(_('light surface'), max_length=7, default='#ffffff', validators=[hex_color_validator])
    light_surface_alt = models.CharField(_('light surface alternate'), max_length=7, default='#f8fafc', validators=[hex_color_validator])
    light_text = models.CharField(_('light text'), max_length=7, default='#111827', validators=[hex_color_validator])
    light_text_soft = models.CharField(_('light secondary text'), max_length=7, default='#475569', validators=[hex_color_validator])
    light_muted = models.CharField(_('light muted text'), max_length=7, default='#64748b', validators=[hex_color_validator])
    light_border = models.CharField(_('light border'), max_length=7, default='#cbd5e1', validators=[hex_color_validator])

    sidebar_width = models.PositiveSmallIntegerField(_('sidebar width'), default=272, validators=[MinValueValidator(220), MaxValueValidator(360)])
    sidebar_collapsed_width = models.PositiveSmallIntegerField(_('collapsed sidebar width'), default=78, validators=[MinValueValidator(64), MaxValueValidator(110)])
    topbar_height = models.PositiveSmallIntegerField(_('topbar height'), default=64, validators=[MinValueValidator(52), MaxValueValidator(88)])
    border_radius = models.PositiveSmallIntegerField(_('border radius'), default=10, validators=[MinValueValidator(4), MaxValueValidator(24)])
    content_spacing_x = models.PositiveSmallIntegerField(_('content horizontal spacing'), default=24, validators=[MinValueValidator(12), MaxValueValidator(42)])
    content_spacing_y = models.PositiveSmallIntegerField(_('content vertical spacing'), default=22, validators=[MinValueValidator(10), MaxValueValidator(42)])
    font_family = models.CharField(
        _('font family'),
        max_length=220,
        blank=True,
        help_text=_('CSS font-family value. Leave empty for the local Persian stack.'),
    )

    compact_mode = models.BooleanField(_('compact mode'), default=False)
    enable_sidebar_collapse = models.BooleanField(_('enable sidebar collapse'), default=True)
    default_sidebar_state = models.CharField(_('default sidebar state'), max_length=12, choices=SIDEBAR_STATE_CHOICES, default=SIDEBAR_EXPANDED)
    show_global_search = models.BooleanField(_('show global search'), default=True)
    show_theme_toggle = models.BooleanField(_('show theme toggle'), default=True)
    show_dashboard_reports = models.BooleanField(_('show dashboard reports'), default=True)
    show_recent_actions = models.BooleanField(_('show recent actions'), default=True)

    custom_css = models.TextField(
        _('extra CSS'),
        blank=True,
        help_text=_('Optional trusted CSS appended after Nova variables.'),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Nova admin theme')
        verbose_name_plural = _('Nova admin themes')
        ordering = ('-is_active', '-updated_at')

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.sidebar_collapsed_width >= self.sidebar_width:
            from django.core.exceptions import ValidationError
            raise ValidationError({'sidebar_collapsed_width': _('Collapsed width must be smaller than sidebar width.')})

    @property
    def resolved_font_family(self):
        return self.font_family or 'Vazirmatn, Vazir, IRANSans, Shabnam, Tahoma, Arial, sans-serif'
