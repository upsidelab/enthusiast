from django.conf import settings
from .models import CustomUser

class ServiceAccountNameService:
    def generate_service_account_email(self, name: str) -> str:
        """
        Generate a service account email based on the provided name.
        """
        return f"{name}@{settings.SERVICE_ACCOUNT_DOMAIN}"

    def is_service_account_name_available(self, name: str) -> bool:
        """
        Check if the provided service account name is available.
        """
        email = self.generate_service_account_email(name)
        return not CustomUser.objects.filter(email=email).exists()