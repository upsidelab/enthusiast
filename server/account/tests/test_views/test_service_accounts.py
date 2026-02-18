import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token

from account.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("service_account_list")


@pytest.fixture
def detail_url(service_account):
    return f"/api/service_accounts/{service_account.id}"


@pytest.fixture
def reset_token_url(service_account):
    return reverse("reset_token", kwargs={"id": service_account.id})


@pytest.fixture
def check_name_url():
    return reverse("check_service_name")


@pytest.fixture
def service_account():
    return baker.make(User, is_service_account=True)


@pytest.fixture
def payload():
    return {
        "name": "test-service",
        "is_active": True,
        "is_staff": False,
    }


@pytest.fixture
def update_payload():
    return {
        "name": "updated-service",
        "is_active": False,
        "is_staff": True,
    }


@pytest.fixture
def check_name_payload():
    return {"name": "test-service-name"}


class TestServiceAccountListViewGet:
    def test_user_with_view_permission_can_list_service_accounts(self, api_client_with_user_view_permission, url):
        baker.make(User, is_service_account=True, _quantity=2)

        response = api_client_with_user_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 2

    def test_user_without_permission_cannot_list_service_accounts(self, api_client, url):
        baker.make(User, is_service_account=True, _quantity=2)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_only_service_accounts_are_listed(self, api_client_with_user_view_permission, url):
        baker.make(User, is_service_account=True, _quantity=2)
        baker.make(User, is_service_account=False, _quantity=2)

        response = api_client_with_user_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert all(user.get("is_service_account", True) for user in response.data["results"])


class TestServiceAccountListViewPost:
    def test_user_with_add_permission_can_create_service_account(
        self, api_client_with_user_add_permission, url, payload
    ):
        response = api_client_with_user_add_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert User.objects.filter(email__contains="test-service").exists()

    def test_user_without_permission_cannot_create_service_account(self, api_client, url, payload):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email__contains="test-service").exists()

    def test_user_with_only_view_permission_cannot_create_service_account(
        self, api_client_with_user_view_permission, url, payload
    ):
        response = api_client_with_user_view_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email__contains="test-service").exists()

    def test_admin_with_global_permission_can_create_service_account(self, admin_api_client, url, payload):
        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert User.objects.filter(email__contains="test-service").exists()


class TestServiceAccountViewPatch:
    def test_user_with_change_permission_can_update_service_account(
        self, api_client_with_user_change_permission, detail_url, update_payload, service_account
    ):
        response = api_client_with_user_change_permission.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        service_account.refresh_from_db()
        assert service_account.email == f"updated-service@{service_account.email.split('@')[1]}"
        assert service_account.is_active is False
        assert service_account.is_staff is True

    def test_user_without_permission_cannot_update_service_account(
        self, api_client, detail_url, update_payload, service_account
    ):
        original_email = service_account.email

        response = api_client.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        service_account.refresh_from_db()
        assert service_account.email == original_email

    def test_user_with_only_view_permission_cannot_update_service_account(
        self, api_client_with_user_view_permission, detail_url, update_payload, service_account
    ):
        original_email = service_account.email

        response = api_client_with_user_view_permission.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        service_account.refresh_from_db()
        assert service_account.email == original_email

    def test_user_cannot_update_regular_user_as_service_account(self, api_client_with_user_change_permission):
        regular_user = baker.make(User, is_service_account=False)
        url = f"/api/service_accounts/{regular_user.id}"
        payload = {"name": "test-service"}

        response = api_client_with_user_change_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_with_global_permission_can_update_service_account(
        self, admin_api_client, detail_url, update_payload, service_account
    ):
        response = admin_api_client.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK


class TestResetTokenViewPost:
    def test_user_with_change_permission_can_reset_token(
        self, api_client_with_user_change_permission, reset_token_url, service_account
    ):
        old_token, _ = Token.objects.get_or_create(user=service_account)
        old_token_key = old_token.key

        response = api_client_with_user_change_permission.post(reset_token_url)

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert response.data["token"] != old_token_key
        new_token = Token.objects.get(user=service_account)
        assert new_token.key == response.data["token"]

    def test_user_without_permission_cannot_reset_token(self, api_client, reset_token_url, service_account):
        old_token, _ = Token.objects.get_or_create(user=service_account)
        old_token_key = old_token.key

        response = api_client.post(reset_token_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        token = Token.objects.get(user=service_account)
        assert token.key == old_token_key

    def test_user_with_only_view_permission_cannot_reset_token(
        self, api_client_with_user_view_permission, reset_token_url, service_account
    ):
        old_token, _ = Token.objects.get_or_create(user=service_account)
        old_token_key = old_token.key

        response = api_client_with_user_view_permission.post(reset_token_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        token = Token.objects.get(user=service_account)
        assert token.key == old_token_key

    def test_user_cannot_reset_token_for_regular_user(self, api_client_with_user_change_permission):
        regular_user = baker.make(User, is_service_account=False)
        url = reverse("reset_token", kwargs={"id": regular_user.id})

        response = api_client_with_user_change_permission.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_with_global_permission_can_reset_token(self, admin_api_client, reset_token_url, service_account):
        old_token, _ = Token.objects.get_or_create(user=service_account)
        old_token_key = old_token.key

        response = admin_api_client.post(reset_token_url)

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data
        assert response.data["token"] != old_token_key


class TestCheckServiceNameViewPost:
    def test_user_with_view_permission_can_check_service_name(
        self, api_client_with_user_view_permission, check_name_url, check_name_payload
    ):
        response = api_client_with_user_view_permission.post(check_name_url, check_name_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "is_available" in response.data

    def test_user_without_permission_cannot_check_service_name(self, api_client, check_name_url, check_name_payload):
        response = api_client.post(check_name_url, check_name_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_with_global_permission_can_check_service_name(
        self, admin_api_client, check_name_url, check_name_payload
    ):
        response = admin_api_client.post(check_name_url, check_name_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "is_available" in response.data
