import copy
import itertools
import json
import logging
from datetime import datetime, time, timedelta
import urllib.parse
from typing import Any, Callable, Dict, List, Optional, Union

from django.conf import settings
from django.contrib.admin import ListFilter
from django.contrib.admin.helpers import AdminForm, Fieldset, InlineAdminFormSet
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.admin.sites import all_sites
from django.contrib.admin.views.main import PAGE_VAR, ChangeList
from django.contrib.auth import get_user_model
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import AbstractUser
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.base import ModelBase
from django.http import HttpRequest
from django.template import Context, Library
from django.template.defaultfilters import capfirst
from django.template.loader import get_template
from django.templatetags.static import static
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import SafeText, mark_safe
from django.utils.text import get_text_list, slugify
from django.utils.translation import gettext

from .. import version
from ..settings import CHANGEFORM_TEMPLATES, get_settings, get_ui_tweaks
from ..utils import get_admin_url, get_filter_id, has_fieldsets_check, make_menu, order_with_respect_to

User = get_user_model()
register = Library()
logger = logging.getLogger(__name__)



def _get_active_nova_theme():
    """Return active NovaAdminTheme, safely handling first-run migrations."""
    try:
        from jazzmin.models import NovaAdminTheme
        return NovaAdminTheme.objects.filter(is_active=True).order_by('-updated_at').first()
    except Exception:
        return None


def _hex_to_rgb(value: str):
    value = (value or '').strip().lstrip('#')
    if len(value) != 6:
        return (37, 99, 235)
    try:
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (37, 99, 235)


def _rgba(value: str, alpha: float) -> str:
    r, g, b = _hex_to_rgb(value)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _theme_public_config(theme) -> Dict[str, Any]:
    if not theme:
        return {
            'themeMode': 'system',
            'defaultSidebarState': 'expanded',
            'enableSidebarCollapse': True,
        }
    return {
        'themeMode': theme.theme_mode,
        'defaultSidebarState': theme.default_sidebar_state,
        'enableSidebarCollapse': bool(theme.enable_sidebar_collapse),
    }


@register.simple_tag(takes_context=True)
def get_side_menu(context: Context, using: str = "available_apps") -> List[Dict]:
    """
    Get the list of apps and models to render out in the side menu and on the dashboard page

    N.B - Permissions are not checked here, as context["available_apps"] has already been filtered by django
    """
    user = context.get("user")
    if not user:
        return []

    options = get_settings()
    ordering = options.get("order_with_respect_to", [])
    ordering = [x.lower() for x in ordering]

    menu = []
    available_apps = copy.deepcopy(context.get(using, []))

    custom_links = {
        app_name: make_menu(user, links, options, allow_appmenus=False)
        for app_name, links in options.get("custom_links", {}).items()
    }

    for app in available_apps:
        app_label = app["app_label"].lower()
        app_custom_links = custom_links.get(app_label, [])
        app["icon"] = options["icons"].get(app_label, options["default_icon_parents"])
        if app_label in options["hide_apps"]:
            continue

        menu_items = []
        for model in app.get("models", []):
            model_str = "{app_label}.{model}".format(app_label=app_label, model=model["object_name"]).lower()
            if model_str in options.get("hide_models", []):
                continue

            model["url"] = model["admin_url"]
            model["model_str"] = model_str
            model["icon"] = options["icons"].get(model_str, options["default_icon_children"])
            menu_items.append(model)

        menu_items.extend(app_custom_links)

        custom_link_names = [x.get("name", "").lower() for x in app_custom_links]
        model_ordering = list(
            filter(
                lambda x: x.lower().startswith("{}.".format(app_label)) or x.lower() in custom_link_names,
                ordering,
            )
        )

        if len(menu_items):
            if model_ordering:
                menu_items = order_with_respect_to(
                    menu_items,
                    model_ordering,
                    getter=lambda x: x.get("model_str", x.get("name", "").lower()),
                )
            app["models"] = menu_items
            menu.append(app)

    if ordering:
        apps_order = list(filter(lambda x: "." not in x, ordering))
        menu = order_with_respect_to(menu, apps_order, getter=lambda x: x["app_label"].lower())

    return menu


@register.simple_tag
def get_top_menu(user: AbstractUser, admin_site: str = "admin") -> List[Dict]:
    """
    Produce the menu for the top nav bar
    """
    options = get_settings()
    return make_menu(user, options.get("topmenu_links", []), options, allow_appmenus=True, admin_site=admin_site)


@register.simple_tag
def get_user_menu(user: AbstractUser, admin_site: str = "admin") -> List[Dict]:
    """
    Produce the menu for the user dropdown
    """
    options = get_settings()
    return make_menu(user, options.get("usermenu_links", []), options, allow_appmenus=False, admin_site=admin_site)



@register.simple_tag
def get_jazzmin_settings(request: WSGIRequest) -> Dict:
    """
    Get Jazzmin settings, then merge the active NovaAdminTheme values.
    The merge is intentionally defensive so the admin still loads before migrations.
    """
    settings = get_settings()

    if hasattr(request, "current_app"):
        admin_site = {x.name: x for x in all_sites}.get(request.current_app, "admin")
        if not settings["site_title"]:
            settings["site_title"] = admin_site.site_title

        if not settings["site_header"]:
            settings["site_header"] = admin_site.site_header

        if not settings["site_brand"]:
            settings["site_brand"] = admin_site.site_header

    theme = _get_active_nova_theme()
    settings["nova_theme"] = theme
    settings["nova_show_global_search"] = True
    settings["nova_show_theme_toggle"] = True
    settings["nova_show_dashboard_reports"] = True
    settings["nova_show_recent_actions"] = True
    settings["nova_enable_sidebar_collapse"] = True

    if theme:
        if theme.site_title:
            settings["site_title"] = theme.site_title
        if theme.site_header:
            settings["site_header"] = theme.site_header
        if theme.site_brand:
            settings["site_brand"] = theme.site_brand
        if theme.brand_logo:
            settings["site_logo"] = theme.brand_logo
            settings["nova_brand_logo"] = theme.brand_logo
        else:
            settings["nova_brand_logo"] = ""
        if theme.favicon:
            settings["site_icon"] = theme.favicon
        elif theme.brand_logo:
            settings["site_icon"] = theme.brand_logo
        settings["nova_show_global_search"] = bool(theme.show_global_search)
        settings["nova_show_theme_toggle"] = bool(theme.show_theme_toggle)
        settings["nova_show_dashboard_reports"] = bool(theme.show_dashboard_reports)
        settings["nova_show_recent_actions"] = bool(theme.show_recent_actions)
        settings["nova_enable_sidebar_collapse"] = bool(theme.enable_sidebar_collapse)
    else:
        settings["nova_brand_logo"] = ""

    return settings


@register.simple_tag
def get_jazzmin_ui_tweaks() -> Dict:
    """
    Return Jazzmin ui tweaks
    """
    return get_ui_tweaks()


@register.simple_tag
def get_jazzmin_version() -> str:
    """
    Get the version for this package
    """
    return version


@register.simple_tag
def get_user_avatar(user: AbstractUser) -> str:
    """
    For the given user, try to get the avatar image, which can be one of:

        - ImageField on the user model
        - URLField/Charfield on the model
        - A callable that receives the user instance e.g lambda u: u.profile.image.url
    """
    no_avatar = static("jazzmin/img/default.jpg")
    options = get_settings()
    avatar_field_name: Optional[Union[str, Callable]] = options.get("user_avatar")

    if not avatar_field_name:
        return no_avatar

    if callable(avatar_field_name):
        return avatar_field_name(user)

    # If we find the property directly on the user model (imagefield or URLfield)
    avatar_field = getattr(user, avatar_field_name, None)
    if avatar_field:
        if type(avatar_field) == str:
            return avatar_field
        elif hasattr(avatar_field, "url"):
            return avatar_field.url
        elif callable(avatar_field):
            return avatar_field()

    logger.warning("avatar field must be an ImageField/URLField on the user model, or a callable")

    return no_avatar


@register.simple_tag
def jazzmin_paginator_number(change_list: ChangeList, i: int) -> SafeText:
    """
    Generate an individual page index link in a paginated list.
    """
    html_str = ""
    start = i == 1
    end = i == change_list.paginator.num_pages
    spacer = i in (".", "…")
    current_page = i == change_list.page_num

    if start:
        link = change_list.get_query_string({PAGE_VAR: change_list.page_num - 1}) if change_list.page_num > 1 else "#"
        html_str += """
        <li class="page-item previous {disabled}">
            <a class="page-link" href="{link}" data-dt-idx="0" tabindex="0">«</a>
        </li>
        """.format(
            link=link, disabled="disabled" if link == "#" else ""
        )

    if current_page:
        html_str += """
        <li class="page-item active">
            <a class="page-link" href="javascript:void(0);" data-dt-idx="3" tabindex="0">{num}</a>
        </li>
        """.format(
            num=i
        )
    elif spacer:
        html_str += """
        <li class="page-item">
            <a class="page-link" href="javascript:void(0);" data-dt-idx="3" tabindex="0">… </a>
        </li>
        """
    else:
        query_string = change_list.get_query_string({PAGE_VAR: i})
        end = "end" if end else ""
        html_str += """
            <li class="page-item">
            <a href="{query_string}" class="page-link {end}" data-dt-idx="3" tabindex="0">{num}</a>
            </li>
        """.format(
            num=i, query_string=query_string, end=end
        )

    if end:
        link = change_list.get_query_string({PAGE_VAR: change_list.page_num + 1}) if change_list.page_num < i else "#"
        html_str += """
        <li class="page-item next {disabled}">
            <a class="page-link" href="{link}" data-dt-idx="7" tabindex="0">»</a>
        </li>
        """.format(
            link=link, disabled="disabled" if link == "#" else ""
        )

    return format_html(html_str)


@register.simple_tag
def admin_extra_filters(cl: ChangeList) -> Dict:
    """
    Return the dict of used filters which is not included in list_filters form
    """
    used_parameters = list(itertools.chain(*(s.used_parameters.keys() for s in cl.filter_specs)))
    return dict((k, v) for k, v in cl.params.items() if k not in used_parameters)


@register.simple_tag
def jazzmin_list_filter(cl: ChangeList, spec: ListFilter) -> SafeText:
    """
    Render out our list filter in a dropdown friendly format, for use by filter.html, see original implementation here

    django.contrib.admin.templatetags.admin_list.admin_list_filter

    """
    tpl = get_template(spec.template)
    choices = list(spec.choices(cl))
    field_key = get_filter_id(spec)
    matched_key = field_key

    for choice in choices:
        qs = choice.get("query_string")
        if not qs:
            continue

        value = ""
        matches = {}
        query_parts = urllib.parse.parse_qs(qs[1:])
        for key in query_parts.keys():
            if key == field_key:
                value = query_parts[key][0]
                matched_key = key
            elif key.startswith(field_key + "__") or "__" + field_key + "__" in key:
                value = query_parts[key][0]
                matched_key = key

            if value:
                matches[matched_key] = value

        # Iterate matches, use original as actual values, additional for hidden
        i = 0
        for key, value in matches.items():
            if i == 0:
                choice["name"] = key
                choice["value"] = value
            i += 1

    return tpl.render({"field_name": field_key, "title": spec.title, "choices": choices, "spec": spec})


@register.simple_tag
def jazzy_admin_url(value: Union[str, ModelBase], admin_site: str = "admin") -> str:
    """
    Get the admin url for a given object
    """
    return get_admin_url(value, admin_site=admin_site)


@register.filter
def has_jazzmin_setting(settings: Dict[str, Any], key: str) -> bool:
    return key in settings and settings[key] is not None


@register.filter
def has_fieldsets(adminform: AdminForm) -> bool:
    """
    Do we have fieldsets
    """
    return has_fieldsets_check(adminform)


@register.simple_tag
def get_sections(
    admin_form: AdminForm, inline_admin_formsets: List[InlineAdminFormSet]
) -> List[Union[Fieldset, InlineAdminFormSet]]:
    """
    Get and sort all of the sections that need rendering out in a change form
    """
    fieldsets = [x for x in admin_form]

    # Make inlines behave like formsets
    for fieldset in inline_admin_formsets:
        fieldset.name = capfirst(fieldset.opts.verbose_name_plural)
        fieldset.is_inline = True
        fieldsets.append(fieldset)

    if hasattr(admin_form.model_admin, "jazzmin_section_order"):
        fieldsets = order_with_respect_to(
            fieldsets, admin_form.model_admin.jazzmin_section_order, getter=lambda x: x.name
        )

    return fieldsets


@register.filter
def remove_lang(url: str, language_code: str) -> str:
    """
    Remove the language code from the url, if we have one
    """
    return url.replace(language_code + "/", "")


@register.filter
def debug(value: Any) -> Any:
    """
    Add in a breakpoint() here and use filter in templates for debugging ;)
    """
    return type(value)


@register.filter
def as_json(value: Union[List, Dict]) -> str:
    """
    Take the given item and dump it out as JSON
    """
    return json.dumps(value)


@register.simple_tag
def get_changeform_template(adminform: AdminForm) -> str:
    """
    Go get the correct change form template based on the modeladmin being used,
    the default template, or the overridden one for this modeladmin
    """
    options = get_settings()
    has_fieldsets = has_fieldsets_check(adminform)
    inlines = adminform.model_admin.inlines
    has_inlines = inlines and len(inlines) > 0
    model = adminform.model_admin.model
    model_name = "{}.{}".format(model._meta.app_label, model._meta.model_name).lower()

    changeform_format = options.get("changeform_format", "")
    if model_name in options.get("changeform_format_overrides", {}):
        changeform_format = options["changeform_format_overrides"][model_name]

    if not has_fieldsets and not has_inlines:
        return CHANGEFORM_TEMPLATES["single"]

    if not changeform_format or changeform_format not in CHANGEFORM_TEMPLATES.keys():
        return CHANGEFORM_TEMPLATES["horizontal_tabs"]

    return CHANGEFORM_TEMPLATES[changeform_format]


@register.simple_tag
def sidebar_status(request: HttpRequest) -> str:
    """
    Check if our sidebar is open or closed
    """

    if request.COOKIES.get("jazzy_menu", "") == "closed":
        return "sidebar-collapse"
    return ""


@register.filter
def can_view_self(perms: PermWrapper) -> bool:
    """
    Determines whether a user has sufficient permissions to view its own profile
    """
    view_perm = "view_{}".format(User._meta.model_name)
    return perms[User._meta.app_label][view_perm]


@register.simple_tag
def header_class(header: Dict, forloop: Dict) -> str:
    """
    Adds CSS classes to header HTML element depending on its attributes
    """
    classes = []
    sorted, asc, desc = (
        header.get("sorted"),
        header.get("ascending"),
        header.get("descending"),
    )

    if forloop["counter0"] == 0:
        classes.append("djn-checkbox-select-all")

    if not header["sortable"]:
        return " ".join(classes)

    if sorted and asc:
        classes.append("sorting_asc")
    elif sorted and desc:
        classes.append("sorting_desc")
    else:
        classes.append("sorting")

    return " ".join(classes)


@register.filter
def app_is_installed(app: str) -> bool:
    """
    Checks if an app has been installed under INSTALLED_APPS on the project settings
    """
    return app in settings.INSTALLED_APPS


@register.simple_tag
def action_message_to_list(action: LogEntry) -> List[Dict]:
    """
    Retrieves a formatted list with all actions taken by a user given a log entry object
    """
    messages = []

    def added(x: str) -> Dict:
        return {
            "msg": x,
            "icon": "plus-circle",
            "colour": "success",
        }

    def changed(x: str) -> Dict:
        return {
            "msg": x,
            "icon": "edit",
            "colour": "blue",
        }

    def deleted(x: str) -> Dict:
        return {
            "msg": x,
            "icon": "trash",
            "colour": "danger",
        }

    if action.change_message and action.change_message[0] == "[":
        try:
            change_message = json.loads(action.change_message)
        except json.JSONDecodeError:
            return [action.change_message]

        for sub_message in change_message:
            if "added" in sub_message:
                if sub_message["added"]:
                    sub_message["added"]["name"] = gettext(sub_message["added"]["name"])
                    messages.append(added(gettext("Added {name} “{object}”.").format(**sub_message["added"])))
                else:
                    messages.append(added(gettext("Added.")))

            elif "changed" in sub_message:
                sub_message["changed"]["fields"] = get_text_list(
                    [gettext(field_name) for field_name in sub_message["changed"]["fields"]],
                    gettext("and"),
                )
                if "name" in sub_message["changed"]:
                    sub_message["changed"]["name"] = gettext(sub_message["changed"]["name"])
                    messages.append(changed(gettext("Changed {fields}.").format(**sub_message["changed"])))
                else:
                    messages.append(changed(gettext("Changed {fields}.").format(**sub_message["changed"])))

            elif "deleted" in sub_message:
                sub_message["deleted"]["name"] = gettext(sub_message["deleted"]["name"])
                messages.append(deleted(gettext("Deleted “{object}”.").format(**sub_message["deleted"])))

    return messages if len(messages) else [changed(gettext(action.change_message))]


@register.filter
def style_bold_first_word(message: str) -> SafeText:
    """
    Wraps first word in a message with <strong> HTML element
    """
    message_words = escape(message).split()

    if not len(message_words):
        return ""

    message_words[0] = "<strong>{}</strong>".format(message_words[0])

    message = " ".join([word for word in message_words])

    return mark_safe(message)


@register.filter
def unicode_slugify(message: str) -> str:
    return slugify(message, allow_unicode=True)


@register.simple_tag
def nova_theme_css() -> SafeText:
    """Return CSS variables from the active NovaAdminTheme if its table exists."""
    theme = _get_active_nova_theme()
    if not theme:
        return mark_safe("")

    radius = int(theme.border_radius)
    dark_border = _rgba(theme.dark_border, .58)
    dark_border_strong = _rgba(theme.dark_border, .82)
    light_border = _rgba(theme.light_border, .72)
    light_border_strong = _rgba(theme.light_border, .95)
    primary_soft = _rgba(theme.primary_color, .14)
    success_soft = _rgba(theme.success_color, .13)
    warning_soft = _rgba(theme.warning_color, .14)
    danger_soft = _rgba(theme.danger_color, .14)
    info_soft = _rgba(theme.info_color, .14)
    font_family = escape(theme.resolved_font_family)

    compact_css = ''
    if theme.compact_mode:
        compact_css = 'body.nova-admin { --content-x: 18px; --content-y: 16px; font-size: 13px; }'

    custom_css = theme.custom_css or ''
    css = f"""
    <style id="nova-db-theme">
      :root {{
        --nova-font: {font_family};
        --primary: {escape(theme.primary_color)};
        --primary-600: {escape(theme.primary_hover_color)};
        --primary-soft: {primary_soft};
        --info: {escape(theme.info_color)};
        --info-soft: {info_soft};
        --success: {escape(theme.success_color)};
        --success-soft: {success_soft};
        --warning: {escape(theme.warning_color)};
        --warning-soft: {warning_soft};
        --danger: {escape(theme.danger_color)};
        --danger-soft: {danger_soft};
        --bg: {escape(theme.dark_background)};
        --bg-soft: {escape(theme.dark_surface)};
        --surface: { _rgba(theme.dark_surface, .86) };
        --surface-solid: {escape(theme.dark_surface)};
        --surface-2: { _rgba(theme.dark_surface_alt, .78) };
        --field: { _rgba(theme.dark_surface, .94) };
        --field-hover: { _rgba(theme.dark_surface_alt, .96) };
        --border: {dark_border};
        --border-strong: {dark_border_strong};
        --text: {escape(theme.dark_text)};
        --text-soft: {escape(theme.dark_text_soft)};
        --muted: {escape(theme.dark_muted)};
        --sidebar-w: {int(theme.sidebar_width)}px;
        --sidebar-mini-w: {int(theme.sidebar_collapsed_width)}px;
        --topbar-h: {int(theme.topbar_height)}px;
        --content-x: {int(theme.content_spacing_x)}px;
        --content-y: {int(theme.content_spacing_y)}px;
        --radius-xs: {max(radius - 4, 4)}px;
        --radius-sm: {max(radius - 2, 4)}px;
        --radius-md: {radius}px;
        --radius-lg: {radius + 4}px;
        --ring: 0 0 0 3px { _rgba(theme.primary_color, .18) };
      }}
      :root[data-theme="light"] {{
        --bg: {escape(theme.light_background)};
        --bg-soft: {escape(theme.light_surface_alt)};
        --surface: { _rgba(theme.light_surface, .92) };
        --surface-solid: {escape(theme.light_surface)};
        --surface-2: { _rgba(theme.light_surface_alt, .95) };
        --field: {escape(theme.light_surface)};
        --field-hover: {escape(theme.light_surface_alt)};
        --border: {light_border};
        --border-strong: {light_border_strong};
        --text: {escape(theme.light_text)};
        --text-soft: {escape(theme.light_text_soft)};
        --muted: {escape(theme.light_muted)};
      }}
      {compact_css}
      {custom_css}
    </style>
    """
    return mark_safe(css)


@register.simple_tag
def nova_theme_config() -> SafeText:
    theme = _get_active_nova_theme()
    return format_html('<script id="nova-admin-config">window.NOVA_ADMIN_CONFIG = {};</script>', mark_safe(json.dumps(_theme_public_config(theme))))


@register.simple_tag
def dashboard_summary(app_list):
    """Return compact dashboard counts for report cards."""
    return dashboard_report_data(app_list)["summary"]


@register.simple_tag
def dashboard_report_data(app_list):
    """
    Build permission-aware dashboard reporting data without third-party chart dependencies.
    The output is intentionally precomputed so templates stay simple and safe.
    """
    apps = list(app_list or [])
    app_rows = []
    model_count = 0
    addable_count = 0
    viewable_count = 0

    for app in apps:
        if not isinstance(app, dict):
            continue
        models = app.get("models", []) or []
        app_model_count = len(models)
        app_addable = sum(1 for model in models if model.get("add_url"))
        app_viewable = sum(1 for model in models if model.get("url") or model.get("admin_url"))
        model_count += app_model_count
        addable_count += app_addable
        viewable_count += app_viewable
        app_rows.append({
            "name": app.get("name") or app.get("app_label") or gettext("Application"),
            "label": app.get("app_label") or "",
            "models": app_model_count,
            "addable": app_addable,
            "viewable": app_viewable,
        })

    max_models = max([row["models"] for row in app_rows] or [1])
    max_addable = max([row["addable"] for row in app_rows] or [1])
    max_viewable = max([row["viewable"] for row in app_rows] or [1])
    for row in app_rows:
        row["model_percent"] = max(4, round((row["models"] / max_models) * 100)) if row["models"] else 4
        row["addable_percent"] = max(4, round((row["addable"] / max_addable) * 100)) if row["addable"] else 4
        row["viewable_percent"] = max(4, round((row["viewable"] / max_viewable) * 100)) if row["viewable"] else 4

    app_rows = sorted(app_rows, key=lambda item: (item["models"], item["addable"], item["name"]), reverse=True)
    top_apps = app_rows[:8]

    today = timezone.localdate()
    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    action_counts = {day: 0 for day in days}
    additions = changes = deletions = 0

    try:
        start = datetime.combine(days[0], time.min)
        if getattr(settings, "USE_TZ", False):
            start = timezone.make_aware(start)
        entries = LogEntry.objects.filter(action_time__gte=start).only("action_time", "action_flag")
        for entry in entries:
            entry_time = entry.action_time
            day = timezone.localtime(entry_time).date() if timezone.is_aware(entry_time) else entry_time.date()
            if day in action_counts:
                action_counts[day] += 1
            if entry.action_flag == ADDITION:
                additions += 1
            elif entry.action_flag == CHANGE:
                changes += 1
            elif entry.action_flag == DELETION:
                deletions += 1
    except Exception:
        additions = changes = deletions = 0

    trend_values = [action_counts[day] for day in days]
    max_trend = max(trend_values or [0]) or 1
    chart_width = 360
    chart_height = 128
    chart_left = 18
    chart_right = 342
    chart_top = 20
    chart_bottom = 104
    denominator = max(len(days) - 1, 1)
    trend_points = []
    for index, day in enumerate(days):
        x = chart_left + round(((chart_right - chart_left) / denominator) * index, 2)
        y = chart_bottom - round((action_counts[day] / max_trend) * (chart_bottom - chart_top), 2)
        trend_points.append({
            "x": x,
            "y": y,
            "count": action_counts[day],
            "date": day,
            "label": day.strftime("%m/%d"),
        })
    if trend_points:
        line_path = "M " + " L ".join(f'{point["x"]} {point["y"]}' for point in trend_points)
        area_path = line_path + f' L {chart_right} {chart_bottom} L {chart_left} {chart_bottom} Z'
    else:
        line_path = ""
        area_path = ""

    total_actions = additions + changes + deletions
    if total_actions:
        add_percent = round((additions / total_actions) * 100)
        change_percent = round((changes / total_actions) * 100)
        delete_percent = max(0, 100 - add_percent - change_percent)
    else:
        add_percent = change_percent = delete_percent = 0

    add_stop = add_percent
    change_stop = add_percent + change_percent
    if total_actions:
        donut_gradient = (
            f"conic-gradient(var(--success) 0 {add_stop}%, "
            f"var(--primary) {add_stop}% {change_stop}%, "
            f"var(--danger) {change_stop}% 100%)"
        )
    else:
        donut_gradient = "conic-gradient(var(--border) 0 100%)"

    model_density = round(model_count / max(len(apps), 1), 1) if apps else 0
    coverage = round((viewable_count / max(model_count, 1)) * 100) if model_count else 0
    add_coverage = round((addable_count / max(model_count, 1)) * 100) if model_count else 0

    return {
        "summary": {
            "apps": len(apps),
            "models": model_count,
            "addable": addable_count,
            "viewable": viewable_count,
            "model_density": model_density,
            "coverage": coverage,
            "add_coverage": add_coverage,
        },
        "apps": top_apps,
        "trend": {
            "points": trend_points,
            "line_path": line_path,
            "area_path": area_path,
            "max": max_trend,
            "total": sum(trend_values),
        },
        "actions": {
            "total": total_actions,
            "additions": additions,
            "changes": changes,
            "deletions": deletions,
            "add_percent": add_percent,
            "change_percent": change_percent,
            "delete_percent": delete_percent,
            "donut_gradient": donut_gradient,
        },
    }
