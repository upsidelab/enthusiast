from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from account.serializers import CreateUpdateServiceAccountSerializer


class Command(BaseCommand):
    help = "Creates service account with admin permission and outputs it's token."

    def add_arguments(self, parser):
        parser.add_argument("-n", "--name", required=True, help="name of service account")

    def handle(self, *args, **options):
        serializer = CreateUpdateServiceAccountSerializer(
            data={"name": options["name"], "is_staff": True, "data_set_ids": []}
        )
        serializer.is_valid(raise_exception=True)
        service_account = serializer.save()
        token, _ = Token.objects.get_or_create(user=service_account)
        print("Service Account token:", token.key)
