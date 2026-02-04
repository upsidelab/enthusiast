import pytest

from account.models import User
from account.services.sso_provider import SSOProviderService


class TestSSOProviderServiceIsEnabled:
    def test_returns_false_when_backend_not_configured(self, settings):
        settings.DEFAULT_SSO_PROVIDER_BACKEND = ""
        assert SSOProviderService.is_enabled() is False

    def test_returns_false_when_backend_setting_missing(self):
        assert SSOProviderService.is_enabled() is False

    def test_returns_true_when_backend_configured(self, settings):
        settings.DEFAULT_SSO_PROVIDER_BACKEND = "social_core.backends.google.GoogleOAuth2"
        assert SSOProviderService.is_enabled() is True


class TestSSOProviderServiceLogin:
    def test_redirects_to_backend_login_url(self, settings):
        settings.DEFAULT_SSO_PROVIDER_BACKEND = "account.tests.test_services.test_sso_provider.FakeBackend"
        response = SSOProviderService.login()
        assert response.url == "/login/fake-backend/"


class TestSSOProviderServiceUpdateUser:
    @pytest.mark.django_db
    def test_raises_not_implemented_error(self):
        from model_bakery import baker

        user = baker.make(User, email="test@example.com")
        with pytest.raises(NotImplementedError):
            SSOProviderService.update_user(user)


class FakeBackend:
    name = "fake-backend"
