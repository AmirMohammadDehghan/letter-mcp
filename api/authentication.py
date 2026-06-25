"""Custom authentication backends for machine-to-machine API access."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from .models import ServiceAPIKey


class ServiceAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticate trusted automation clients such as n8n with a service API key.

    Supported headers:
    - X-API-Key: n8n_xxx
    - Authorization: Api-Key n8n_xxx

    The key is mapped to a Django user, so the existing owner-scoped selectors
    keep working exactly like JWT-authenticated requests.
    """

    keyword = "Api-Key"
    header_name = "HTTP_X_API_KEY"

    def authenticate(self, request):
        raw_key = self._get_key_from_request(request)
        if not raw_key:
            return None

        key_prefix = raw_key[:12]
        try:
            service_key = ServiceAPIKey.objects.select_related("owner").get(
                key_prefix=key_prefix,
                is_active=True,
            )
        except ServiceAPIKey.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed(_("Invalid API key.")) from exc

        if service_key.is_expired:
            raise exceptions.AuthenticationFailed(_("Expired API key."))

        if not service_key.matches(raw_key):
            raise exceptions.AuthenticationFailed(_("Invalid API key."))

        if not service_key.owner.is_active:
            raise exceptions.AuthenticationFailed(_("API key owner is inactive."))

        service_key.mark_used()
        return (service_key.owner, service_key)

    def _get_key_from_request(self, request) -> str | None:
        x_api_key = request.META.get(self.header_name)
        if x_api_key:
            return x_api_key.strip()

        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == self.keyword.lower():
            return parts[1].strip()

        return None
