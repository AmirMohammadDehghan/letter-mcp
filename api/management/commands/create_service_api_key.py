"""Create a hashed service API key for n8n or another automation client."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from api.models import ServiceAPIKey

User = get_user_model()


class Command(BaseCommand):
    help = "Create a service API key and print the raw key exactly once."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username that owns templates/documents.")
        parser.add_argument("--name", default="n8n", help="Human-readable API key name.")
        parser.add_argument(
            "--created-by",
            default=None,
            help="Optional username that created this key for auditing.",
        )
        parser.add_argument(
            "--source",
            action="append",
            dest="sources",
            default=[],
            help="Allowed source value. Repeatable. Example: --source n8n",
        )
        parser.add_argument(
            "--expires-days",
            type=int,
            default=None,
            help="Optional expiration in days from now.",
        )

    def handle(self, *args, **options):
        try:
            owner = User.objects.get(username=options["owner"])
        except User.DoesNotExist as exc:
            raise CommandError(f"Owner user not found: {options['owner']}") from exc

        created_by = None
        if options.get("created_by"):
            try:
                created_by = User.objects.get(username=options["created_by"])
            except User.DoesNotExist as exc:
                raise CommandError(f"Creator user not found: {options['created_by']}") from exc

        expires_at = None
        if options.get("expires_days"):
            expires_at = timezone.now() + timezone.timedelta(days=options["expires_days"])

        service_key, raw_key = ServiceAPIKey.build(
            owner=owner,
            name=options["name"],
            created_by=created_by,
            allowed_sources=options.get("sources") or [],
            expires_at=expires_at,
        )

        self.stdout.write(self.style.SUCCESS("Service API key created successfully."))
        self.stdout.write(f"Owner: {owner.username}")
        self.stdout.write(f"Name: {service_key.name}")
        self.stdout.write(f"Prefix: {service_key.key_prefix}")
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Copy this raw key now. It will never be shown again:"))
        self.stdout.write(raw_key)
