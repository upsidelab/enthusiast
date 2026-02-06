from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from utils.functions import import_from_string

User = get_user_model()


class SSOProviderService:
    NOT_CONFIGURED_ERROR_MESSAGE = "SSO provider service not configured."

    @staticmethod
    def login():
        backend = import_from_string(settings.DEFAULT_SSO_PROVIDER_BACKEND)
        return redirect(f"/login/{backend.name}/")

    @staticmethod
    def is_enabled() -> bool:
        return bool(getattr(settings, "DEFAULT_SSO_PROVIDER_BACKEND", ""))

    @staticmethod
    def update_user(user: User):
        raise NotImplementedError
