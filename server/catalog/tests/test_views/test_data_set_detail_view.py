import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from catalog.models import DataSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def url(data_set):
    return reverse("data_set_detail", kwargs={"data_set_id": data_set.id})


class TestDataSetDetailViewGet:
    def test_user_with_view_permission_can_access_dataset(self, api_client_with_view_permission, url, data_set):
        response = api_client_with_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == data_set.id

    def test_user_without_permission_cannot_access_dataset(self, api_client, url, data_set):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_with_global_view_permission_can_access_any_dataset(self, admin_api_client, data_set):
        other_data_set = baker.make(DataSet)
        url = reverse("data_set_detail", kwargs={"data_set_id": other_data_set.id})

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == other_data_set.id

    def test_user_with_object_level_permission_cannot_access_other_datasets(
        self, api_client_with_view_permission, data_set
    ):
        other_data_set = baker.make(DataSet)
        url = reverse("data_set_detail", kwargs={"data_set_id": other_data_set.id})

        response = api_client_with_view_permission.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetDetailViewPatch:
    @pytest.fixture
    def payload(self):
        return {"name": "Updated DataSet Name"}

    def test_user_with_change_permission_can_update_dataset(
        self, api_client_with_change_permission, url, payload, data_set
    ):
        response = api_client_with_change_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated DataSet Name"
        data_set.refresh_from_db()
        assert data_set.name == "Updated DataSet Name"

    def test_user_with_view_only_permission_cannot_update_dataset(
        self, api_client_with_view_permission, url, payload, data_set
    ):
        response = api_client_with_view_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        data_set.refresh_from_db()
        assert data_set.name != "Updated DataSet Name"

    def test_user_without_permission_cannot_update_dataset(self, api_client, url, payload, data_set):
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_with_object_level_change_permission_cannot_update_other_datasets(
        self, api_client_with_change_permission, payload, data_set
    ):
        other_data_set = baker.make(DataSet)
        url = reverse("data_set_detail", kwargs={"data_set_id": other_data_set.id})

        response = api_client_with_change_permission.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_with_global_permission_can_update_any_dataset(self, admin_api_client, payload, data_set):
        other_data_set = baker.make(DataSet)
        url = reverse("data_set_detail", kwargs={"data_set_id": other_data_set.id})

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated DataSet Name"
