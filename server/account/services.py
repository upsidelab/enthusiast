from abc import ABC, abstractmethod

from django.conf import settings
from rest_framework.authtoken.models import Token

from .models import User


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
        return not User.objects.filter(email=email).exists()


class OTPLoginService(ABC):
    NOT_CONFIGURED_ERROR_MESSAGE = "OTP service not configured."

    def create_user(self, email: str) -> User:
        user, _ = User.objects.get_or_create(email=email)
        return user

    def create_token(self, user: User) -> Token:
        token, _ = Token.objects.get_or_create(user=user)
        return token

    @abstractmethod
    def get_email_from_token(self, token: str) -> str:
        pass

    @abstractmethod
    def get_redirect_url(self) -> str:
        pass

    @abstractmethod
    def get_token(self, code: str) -> str:
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        pass
