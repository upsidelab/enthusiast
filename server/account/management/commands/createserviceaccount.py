from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from account.serializers import CreateUpdateServiceAccountSerializer
from catalog.models import DataSet


class Command(BaseCommand):
    help = "Creates service account and outputs it's token."

    def add_arguments(self, parser):
        parser.add_argument("-n", "--name", required=True, help="name of service account")
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            "-d",
            "--datasets",
            nargs="+",
            default=[],
            type=int,
            help="optional list of dataset ids, if none is passed, all datasets will be added.",
        )
        group.add_argument(
            "--admin",
            action="store_true",
            help="option to create service account with admin permission",
        )

    def handle(self, *args, **options):
        admin = options["admin"]
        datasets = options["datasets"]
        if not datasets and not admin:
            datasets = DataSet.objects.all().values_list("id", flat=True)

        serializer = CreateUpdateServiceAccountSerializer(
            data={"name": options["name"], "is_staff": admin, "data_set_ids": datasets}
        )
        serializer.is_valid(raise_exception=True)
        service_account = serializer.save()
        token, _ = Token.objects.get_or_create(user=service_account)
        print("Service Account token:", token.key)
