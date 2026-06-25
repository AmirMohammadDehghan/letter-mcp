from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='NovaAdminTheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default', max_length=80, verbose_name='theme name')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('site_title', models.CharField(blank=True, max_length=120, verbose_name='site title')),
                ('site_header', models.CharField(blank=True, max_length=120, verbose_name='site header')),
                ('site_brand', models.CharField(blank=True, max_length=80, verbose_name='site brand')),
                ('primary_color', models.CharField(default='#3b82f6', max_length=7, verbose_name='primary color')),
                ('info_color', models.CharField(default='#0891b2', max_length=7, verbose_name='info color')),
                ('success_color', models.CharField(default='#16a34a', max_length=7, verbose_name='success color')),
                ('warning_color', models.CharField(default='#d97706', max_length=7, verbose_name='warning color')),
                ('danger_color', models.CharField(default='#dc2626', max_length=7, verbose_name='danger color')),
                ('dark_background', models.CharField(default='#0b1220', max_length=7, verbose_name='dark background')),
                ('light_background', models.CharField(default='#f4f7fb', max_length=7, verbose_name='light background')),
                ('sidebar_width', models.PositiveSmallIntegerField(default=272, verbose_name='sidebar width')),
                ('sidebar_collapsed_width', models.PositiveSmallIntegerField(default=78, verbose_name='collapsed sidebar width')),
                ('border_radius', models.PositiveSmallIntegerField(default=12, verbose_name='border radius')),
                ('compact_mode', models.BooleanField(default=False, verbose_name='compact mode')),
                ('show_recent_actions', models.BooleanField(default=True, verbose_name='show recent actions')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Nova admin theme', 'verbose_name_plural': 'Nova admin themes'},
        ),
    ]
