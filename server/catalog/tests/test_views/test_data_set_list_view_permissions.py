import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from account.services import UserService
from catalog.models import DataSet
from catalog.utils import AdminRole, UserRole

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("data_set_list")


@pytest.fixture
def payload():
    return {"name": "New DataSet"}


class TestDataSetListViewGet:
    def test_user_with_view_permission_sees_only_accessible_datasets(self, api_client, user, url):
        accessible_dataset = baker.make(DataSet)
        inaccessible_dataset = baker.make(DataSet)
        UserService.assign_role(user, UserRole, accessible_dataset)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        dataset_ids = [ds["id"] for ds in response.data["results"]]
        assert accessible_dataset.id in dataset_ids
        assert inaccessible_dataset.id not in dataset_ids

    def test_user_without_permissions_sees_no_datasets(self, api_client, url):
        baker.make(DataSet, _quantity=3)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_admin_with_global_permission_sees_all_datasets(self, admin_api_client, url):
        baker.make(DataSet, _quantity=3)

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_user_with_multiple_dataset_permissions_sees_all(self, api_client, user, url):
        dataset1 = baker.make(DataSet)
        dataset2 = baker.make(DataSet)
        dataset3 = baker.make(DataSet)
        UserService.assign_role(user, UserRole, dataset1)
        UserService.assign_role(user, UserRole, dataset2)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        dataset_ids = [ds["id"] for ds in response.data["results"]]
        assert dataset1.id in dataset_ids
        assert dataset2.id in dataset_ids
        assert dataset3.id not in dataset_ids


class TestDataSetListViewPost:
    def test_user_with_add_permission_can_create_dataset(self, api_client, user, url, payload):
        UserService.assign_role(user, AdminRole)

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DataSet.objects.filter(name="New DataSet").exists()

    def test_user_without_add_permission_cannot_create_dataset(self, api_client, url, payload):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not DataSet.objects.filter(name="New DataSet").exists()

    def test_user_with_only_view_permission_cannot_create_dataset(self, api_client, user, url, payload):
        UserService.assign_role(user, UserRole)

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not DataSet.objects.filter(name="New DataSet").exists()

    def test_admin_with_global_add_permission_can_create_dataset(self, admin_api_client, url, payload):
        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DataSet.objects.filter(name="New DataSet").exists()

    def test_created_dataset_includes_creator_in_users(self, api_client, user, url, payload):
        UserService.assign_role(user, AdminRole)

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        dataset = DataSet.objects.get(name="New DataSet")
        assert user in dataset.users.all()
