import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from account.models import User
from account.services import UserService
from catalog.utils import AdminRole

pytestmark = pytest.mark.django_db


@pytest.fixture
def url(data_set):
    return reverse("data_set_user_list", kwargs={"data_set_id": data_set.id})


@pytest.fixture
def delete_url(data_set, user):
    return reverse("data_set_user_details", kwargs={"data_set_id": data_set.id, "user_id": user.id})


class TestDataSetUserListViewGet:
    def test_user_with_manage_permission_can_list_users(self, api_client_with_manage_permission, url, data_set):
        user1 = baker.make(User)
        user2 = baker.make(User)
        data_set.users.add(user1, user2)

        response = api_client_with_manage_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_user_without_manage_permission_cannot_list_users(self, api_client, url, data_set):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_with_view_permission_cannot_list_users(self, api_client_with_view_permission, url, data_set):
        response = api_client_with_view_permission.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_with_global_permission_can_list_users(self, admin_api_client, admin_user, url, data_set):
        UserService.assign_role(admin_user, AdminRole, data_set)
        user1 = baker.make(User)
        data_set.users.add(user1)

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1


class TestDataSetUserListViewPost:
    @pytest.fixture
    def new_user(self):
        return baker.make(User)

    @pytest.fixture
    def payload(self, new_user):
        return {"user_id": new_user.id}

    def test_user_with_manage_permission_can_add_user(
        self, api_client_with_manage_permission, url, payload, data_set, new_user
    ):
        response = api_client_with_manage_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert data_set.users.filter(id=new_user.id).exists()

    def test_user_without_manage_permission_cannot_add_user(self, api_client, url, payload, data_set, new_user):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not data_set.users.filter(id=new_user.id).exists()

    def test_staff_user_gets_admin_role_on_dataset(self, api_client_with_manage_permission, url, data_set):
        staff_user = baker.make(User, is_staff=True)
        payload = {"user_id": staff_user.id}

        response = api_client_with_manage_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        from guardian.shortcuts import get_user_perms

        perms = [str(p) for p in get_user_perms(staff_user, data_set)]
        assert "view_dataset" in perms
        assert "change_dataset" in perms

    def test_regular_user_gets_user_role_on_dataset(self, api_client_with_manage_permission, url, data_set):
        regular_user = baker.make(User, is_staff=False)
        payload = {"user_id": regular_user.id}

        response = api_client_with_manage_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        from guardian.shortcuts import get_user_perms

        perms = [str(p) for p in get_user_perms(regular_user, data_set)]
        assert "view_dataset" in perms
        assert "change_dataset" not in perms

    def test_admin_with_global_permission_can_add_user(
        self, admin_api_client, admin_user, url, payload, data_set, new_user
    ):
        UserService.assign_role(admin_user, AdminRole, data_set)

        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert data_set.users.filter(id=new_user.id).exists()


class TestDataSetUserViewDelete:
    def test_user_with_manage_permission_can_remove_user(
        self, api_client_with_manage_permission, delete_url, data_set, user
    ):
        data_set.users.add(user)

        response = api_client_with_manage_permission.delete(delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not data_set.users.filter(id=user.id).exists()

    def test_user_without_manage_permission_cannot_remove_user(self, api_client, delete_url, data_set, user):
        data_set.users.add(user)

        response = api_client.delete(delete_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert data_set.users.filter(id=user.id).exists()

    def test_admin_with_global_permission_can_remove_user(
        self, admin_api_client, admin_user, delete_url, data_set, user
    ):
        UserService.assign_role(admin_user, AdminRole, data_set)
        data_set.users.add(user)

        response = admin_api_client.delete(delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not data_set.users.filter(id=user.id).exists()
