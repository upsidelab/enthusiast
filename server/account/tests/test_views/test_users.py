import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from account.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("user_list")


@pytest.fixture
def detail_url(user):
    return reverse("user_details", kwargs={"id": user.id})


@pytest.fixture
def password_url(user):
    return reverse("user_password", kwargs={"id": user.id})


@pytest.fixture
def payload():
    return {
        "email": "newuser@example.com",
        "password": "testpass123",
        "is_active": True,
        "is_staff": False,
    }


@pytest.fixture
def update_payload():
    return {
        "email": "updated@example.com",
        "is_active": False,
        "is_staff": True,
    }


@pytest.fixture
def password_payload():
    return {"password": "newpassword123"}


class TestUserListViewGet:
    def test_user_with_view_permission_can_list_users(self, api_client_with_user_view_permission, url):
        baker.make(User, is_service_account=False, _quantity=2)

        response = api_client_with_user_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 2

    def test_user_without_permission_cannot_list_users(self, api_client, url):
        baker.make(User, is_service_account=False, _quantity=2)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_service_accounts_are_excluded_from_list(self, api_client_with_user_view_permission, url):
        baker.make(User, is_service_account=False, _quantity=2)
        baker.make(User, is_service_account=True, _quantity=2)

        response = api_client_with_user_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert all(not user.get("is_service_account", False) for user in response.data["results"])


class TestUserListViewPost:
    def test_user_with_add_permission_can_create_user(self, api_client_with_user_add_permission, url, payload):
        response = api_client_with_user_add_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_user_without_permission_cannot_create_user(self, api_client, url, payload):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email="newuser@example.com").exists()

    def test_user_with_only_view_permission_cannot_create_user(
        self, api_client_with_user_view_permission, url, payload
    ):
        response = api_client_with_user_view_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email="newuser@example.com").exists()

    def test_admin_with_global_permission_can_create_user(self, admin_api_client, url, payload):
        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()


class TestUserViewPatch:
    def test_user_with_change_permission_can_update_user(
        self, api_client_with_user_change_permission, detail_url, update_payload, user
    ):
        response = api_client_with_user_change_permission.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == "updated@example.com"
        assert user.is_active is False
        assert user.is_staff is True

    def test_user_without_permission_cannot_update_user(self, api_client, detail_url, update_payload, user):
        original_email = user.email

        response = api_client.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        user.refresh_from_db()
        assert user.email == original_email

    def test_user_with_only_view_permission_cannot_update_user(
        self, api_client_with_user_view_permission, detail_url, update_payload, user
    ):
        original_email = user.email

        response = api_client_with_user_view_permission.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        user.refresh_from_db()
        assert user.email == original_email

    def test_user_cannot_update_service_account(self, api_client_with_user_change_permission):
        service_account = baker.make(User, is_service_account=True)
        url = reverse("user_details", kwargs={"id": service_account.id})
        payload = {"email": "updated@example.com"}

        response = api_client_with_user_change_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_with_global_permission_can_update_user(self, admin_api_client, detail_url, update_payload, user):
        response = admin_api_client.patch(detail_url, update_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == "updated@example.com"


class TestUserPasswordViewPatch:
    def test_user_with_change_permission_can_update_password(
        self, api_client_with_user_change_permission, password_url, password_payload, user
    ):
        old_password_hash = user.password

        response = api_client_with_user_change_permission.patch(password_url, password_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.password != old_password_hash
        assert user.check_password("newpassword123")

    def test_user_without_permission_cannot_update_password(self, api_client, password_url, password_payload, user):
        old_password_hash = user.password

        response = api_client.patch(password_url, password_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        user.refresh_from_db()
        assert user.password == old_password_hash

    def test_user_with_only_view_permission_cannot_update_password(
        self, api_client_with_user_view_permission, password_url, password_payload, user
    ):
        old_password_hash = user.password

        response = api_client_with_user_view_permission.patch(password_url, password_payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        user.refresh_from_db()
        assert user.password == old_password_hash

    def test_user_cannot_update_service_account_password(self, api_client_with_user_change_permission):
        service_account = baker.make(User, is_service_account=True)
        url = reverse("user_password", kwargs={"id": service_account.id})
        payload = {"password": "newpassword123"}

        response = api_client_with_user_change_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_with_global_permission_can_update_password(
        self, admin_api_client, password_url, password_payload, user
    ):
        old_password_hash = user.password

        response = admin_api_client.patch(password_url, password_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.password != old_password_hash
        assert user.check_password("newpassword123")
