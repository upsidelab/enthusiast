from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Update app labels in django_migrations and django_content_type tables'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("UPDATE django_migrations SET app = 'catalog' WHERE app = 'ecl';")
            cursor.execute("UPDATE django_content_type SET app_label = 'catalog' WHERE app_label = 'ecl';")
        self.stdout.write(self.style.SUCCESS('Successfully updated app labels'))