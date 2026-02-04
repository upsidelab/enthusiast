import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from account.models import User

pytestmark = pytest.mark.django_db


class TestUserListView:
    @pytest.fixture
    def url(self):
        return reverse("user_list")

    def test_full_admin_can_list_users(self, admin_api_client, url, user):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_full_admin_can_create_user(self, admin_api_client, url):
        payload = {
            "email": "newuser@test.com",
            "password": "testpass123",
            "is_active": True,
            "is_staff": False,
        }
        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@test.com").exists()

    def test_limited_admin_cannot_list_users(self, limited_admin_api_client, url):
        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_limited_admin_cannot_create_user(self, limited_admin_api_client, url):
        payload = {
            "email": "newuser@test.com",
            "password": "testpass123",
            "is_active": True,
            "is_staff": False,
        }
        response = limited_admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email="newuser@test.com").exists()

    def test_regular_user_cannot_list_users(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_regular_user_cannot_create_user(self, api_client, url):
        payload = {
            "email": "newuser@test.com",
            "password": "testpass123",
            "is_active": True,
            "is_staff": False,
        }
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not User.objects.filter(email="newuser@test.com").exists()

    def test_service_accounts_are_excluded_from_list(self, admin_api_client, url):
        service_account = baker.make(User, is_service_account=True, email="service@test.com")
        regular_user = baker.make(User, is_service_account=False, email="regular@test.com")

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        user_emails = [u["email"] for u in response.data["results"]]
        assert service_account.email not in user_emails
        assert regular_user.email in user_emails


class TestUserView:
    @pytest.fixture
    def target_user(self):
        return baker.make(User, email="target@test.com", is_active=True, is_staff=False)

    @pytest.fixture
    def url(self, target_user):
        return reverse("user_details", kwargs={"id": target_user.id})

    def test_full_admin_can_update_user(self, admin_api_client, url, target_user):
        payload = {
            "email": "updated@test.com",
            "is_active": True,
            "is_staff": True,
        }
        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        target_user.refresh_from_db()
        assert target_user.email == "updated@test.com"
        assert target_user.is_staff is True

    def test_limited_admin_cannot_update_user(self, limited_admin_api_client, url):
        payload = {
            "email": "updated@test.com",
            "is_active": True,
            "is_staff": True,
        }
        response = limited_admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_regular_user_cannot_update_user(self, api_client, url):
        payload = {
            "email": "updated@test.com",
            "is_active": True,
            "is_staff": True,
        }
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_update_service_account(self, admin_api_client):
        service_account = baker.make(User, is_service_account=True, email="service@test.com")
        url = reverse("user_details", kwargs={"id": service_account.id})
        payload = {"email": "updated@test.com"}

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUserPasswordView:
    @pytest.fixture
    def target_user(self):
        return baker.make(User, email="target@test.com", is_service_account=False)

    @pytest.fixture
    def url(self, target_user):
        return reverse("user_password", kwargs={"id": target_user.id})

    def test_full_admin_can_update_password(self, admin_api_client, url, target_user):
        old_password_hash = target_user.password
        payload = {"password": "newpassword123"}

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        target_user.refresh_from_db()
        assert target_user.password != old_password_hash
        assert target_user.check_password("newpassword123")

    def test_limited_admin_cannot_update_password(self, limited_admin_api_client, url):
        payload = {"password": "newpassword123"}

        response = limited_admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_regular_user_cannot_update_password(self, api_client, url):
        payload = {"password": "newpassword123"}

        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_update_service_account_password(self, admin_api_client):
        service_account = baker.make(User, is_service_account=True, email="service@test.com")
        url = reverse("user_password", kwargs={"id": service_account.id})
        payload = {"password": "newpassword123"}

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
