from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('jazzmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField('novaadmintheme', 'brand_logo', models.CharField(blank=True, help_text='Optional static path, e.g. img/admin-logo.svg or jazzmin/img/default-log.svg.', max_length=180, verbose_name='brand logo static path')),
        migrations.AddField('novaadmintheme', 'favicon', models.CharField(blank=True, help_text='Optional static path for favicon. Leave empty to use the logo.', max_length=180, verbose_name='favicon static path')),
        migrations.AddField('novaadmintheme', 'theme_mode', models.CharField(choices=[('system', 'Follow system preference'), ('dark', 'Dark'), ('light', 'Light')], default='system', max_length=12, verbose_name='default theme mode')),
        migrations.AddField('novaadmintheme', 'primary_hover_color', models.CharField(default='#1d4ed8', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='primary hover color')),
        migrations.AddField('novaadmintheme', 'dark_surface', models.CharField(default='#111827', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark surface')),
        migrations.AddField('novaadmintheme', 'dark_surface_alt', models.CharField(default='#1e293b', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark surface alternate')),
        migrations.AddField('novaadmintheme', 'dark_text', models.CharField(default='#e5e7eb', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark text')),
        migrations.AddField('novaadmintheme', 'dark_text_soft', models.CharField(default='#b6c2d1', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark secondary text')),
        migrations.AddField('novaadmintheme', 'dark_muted', models.CharField(default='#8a98aa', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark muted text')),
        migrations.AddField('novaadmintheme', 'dark_border', models.CharField(default='#334155', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark border')),
        migrations.AddField('novaadmintheme', 'light_surface', models.CharField(default='#ffffff', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light surface')),
        migrations.AddField('novaadmintheme', 'light_surface_alt', models.CharField(default='#f8fafc', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light surface alternate')),
        migrations.AddField('novaadmintheme', 'light_text', models.CharField(default='#111827', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light text')),
        migrations.AddField('novaadmintheme', 'light_text_soft', models.CharField(default='#475569', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light secondary text')),
        migrations.AddField('novaadmintheme', 'light_muted', models.CharField(default='#64748b', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light muted text')),
        migrations.AddField('novaadmintheme', 'light_border', models.CharField(default='#cbd5e1', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light border')),
        migrations.AddField('novaadmintheme', 'topbar_height', models.PositiveSmallIntegerField(default=64, validators=[MinValueValidator(52), MaxValueValidator(88)], verbose_name='topbar height')),
        migrations.AddField('novaadmintheme', 'content_spacing_x', models.PositiveSmallIntegerField(default=24, validators=[MinValueValidator(12), MaxValueValidator(42)], verbose_name='content horizontal spacing')),
        migrations.AddField('novaadmintheme', 'content_spacing_y', models.PositiveSmallIntegerField(default=22, validators=[MinValueValidator(10), MaxValueValidator(42)], verbose_name='content vertical spacing')),
        migrations.AddField('novaadmintheme', 'font_family', models.CharField(blank=True, help_text='CSS font-family value. Leave empty for the local Persian stack.', max_length=220, verbose_name='font family')),
        migrations.AddField('novaadmintheme', 'enable_sidebar_collapse', models.BooleanField(default=True, verbose_name='enable sidebar collapse')),
        migrations.AddField('novaadmintheme', 'default_sidebar_state', models.CharField(choices=[('expanded', 'Expanded'), ('collapsed', 'Collapsed')], default='expanded', max_length=12, verbose_name='default sidebar state')),
        migrations.AddField('novaadmintheme', 'show_global_search', models.BooleanField(default=True, verbose_name='show global search')),
        migrations.AddField('novaadmintheme', 'show_theme_toggle', models.BooleanField(default=True, verbose_name='show theme toggle')),
        migrations.AddField('novaadmintheme', 'show_dashboard_reports', models.BooleanField(default=True, verbose_name='show dashboard reports')),
        migrations.AddField('novaadmintheme', 'custom_css', models.TextField(blank=True, help_text='Optional trusted CSS appended after Nova variables.', verbose_name='extra CSS')),
        migrations.AlterField('novaadmintheme', 'primary_color', models.CharField(default='#2563eb', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='primary color')),
        migrations.AlterField('novaadmintheme', 'info_color', models.CharField(default='#0891b2', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='info color')),
        migrations.AlterField('novaadmintheme', 'success_color', models.CharField(default='#16a34a', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='success color')),
        migrations.AlterField('novaadmintheme', 'warning_color', models.CharField(default='#d97706', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='warning color')),
        migrations.AlterField('novaadmintheme', 'danger_color', models.CharField(default='#dc2626', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='danger color')),
        migrations.AlterField('novaadmintheme', 'dark_background', models.CharField(default='#0b1220', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='dark background')),
        migrations.AlterField('novaadmintheme', 'light_background', models.CharField(default='#f4f7fb', max_length=7, validators=[RegexValidator(message='Enter a valid hex color like #2563eb.', regex='^#[0-9A-Fa-f]{6}$')], verbose_name='light background')),
        migrations.AlterField('novaadmintheme', 'sidebar_width', models.PositiveSmallIntegerField(default=272, validators=[MinValueValidator(220), MaxValueValidator(360)], verbose_name='sidebar width')),
        migrations.AlterField('novaadmintheme', 'sidebar_collapsed_width', models.PositiveSmallIntegerField(default=78, validators=[MinValueValidator(64), MaxValueValidator(110)], verbose_name='collapsed sidebar width')),
        migrations.AlterField('novaadmintheme', 'border_radius', models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(4), MaxValueValidator(24)], verbose_name='border radius')),
        migrations.AlterModelOptions('novaadmintheme', options={'ordering': ('-is_active', '-updated_at'), 'verbose_name': 'Nova admin theme', 'verbose_name_plural': 'Nova admin themes'}),
    ]
