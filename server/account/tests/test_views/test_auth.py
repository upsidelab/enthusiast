from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestSSOProviderLoginView:
    def test_redirects_to_frontend_with_error_when_sso_disabled(self, settings):
        settings.DEFAULT_SSO_PROVIDER_BACKEND = ""
        settings.FRONTEND_BASE_URL = "https://app.example.com"
        client = Client()
        response = client.get(reverse("sso-login"))
        assert response.status_code == 302
        assert response["Location"].startswith("https://app.example.com/login?error=")

    def test_redirects_to_backend_login_when_sso_enabled(self, settings):
        settings.DEFAULT_SSO_PROVIDER_BACKEND = "account.tests.test_services.test_sso_provider.FakeBackend"
        settings.FRONTEND_BASE_URL = "https://app.example.com"
        client = Client()
        response = client.get(reverse("sso-login"))
        assert response.status_code == 302
        assert response["Location"] == "/login/fake-backend/"

    def test_redirects_to_frontend_with_generic_error_on_exception(self, settings):
        settings.FRONTEND_BASE_URL = "https://app.example.com"
        client = Client()
        with patch(
            "account.views.auth.import_from_string",
            side_effect=Exception("Service unavailable"),
        ):
            response = client.get(reverse("sso-login"))
        assert response.status_code == 302
        assert response["Location"].startswith("https://app.example.com/login?error=")
        assert "error=Service+unavailable" in response["Location"]
