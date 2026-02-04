import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from catalog.models import DataSet, DocumentSource

pytestmark = pytest.mark.django_db


@pytest.fixture
def url(data_set):
    return reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})


@pytest.fixture
def detail_url(data_set, document_source):
    return reverse(
        "data_set_document_source_details",
        kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
    )


@pytest.fixture
def payload():
    return {"plugin_name": "Test Source", "config": {}}


class TestDataSetDocumentSourceListViewGet:
    def test_user_with_view_permission_can_list_sources(self, api_client_with_view_permission, url, data_set):
        baker.make(DocumentSource, data_set=data_set, _quantity=2)

        response = api_client_with_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_user_without_permission_cannot_list_sources(self, api_client, url, data_set):
        baker.make(DocumentSource, data_set=data_set, _quantity=2)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_with_view_permission_only_sees_sources_from_their_dataset(
        self, api_client_with_view_permission, data_set
    ):
        other_dataset = baker.make(DataSet)
        baker.make(DocumentSource, data_set=data_set, _quantity=2)
        baker.make(DocumentSource, data_set=other_dataset, _quantity=3)
        url = reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})

        response = api_client_with_view_permission.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


class TestDataSetDocumentSourceListViewPost:
    def test_user_with_change_permission_can_create_source(
        self, api_client_with_change_permission, url, payload, data_set
    ):
        response = api_client_with_change_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DocumentSource.objects.filter(data_set=data_set, plugin_name="Test Source").exists()

    def test_user_without_change_permission_cannot_create_source(self, api_client, url, payload, data_set):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not DocumentSource.objects.filter(data_set=data_set, plugin_name="Test Source").exists()

    def test_user_with_view_only_permission_cannot_create_source(
        self, api_client_with_view_permission, url, payload, data_set
    ):
        response = api_client_with_view_permission.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetDocumentSourceViewGet:
    def test_user_with_view_permission_can_get_source(
        self, api_client_with_view_permission, detail_url, document_source
    ):
        response = api_client_with_view_permission.get(detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == document_source.id

    def test_user_without_permission_cannot_get_source(self, api_client, detail_url, document_source):
        response = api_client.get(detail_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetDocumentSourceViewPatch:
    @pytest.fixture
    def payload(self):
        return {"plugin_name": "Updated Source"}

    def test_user_with_change_permission_can_update_source(
        self, api_client_with_change_permission, detail_url, payload, document_source
    ):
        response = api_client_with_change_permission.patch(detail_url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        document_source.refresh_from_db()
        assert document_source.plugin_name == "Updated Source"

    def test_user_without_change_permission_cannot_update_source(
        self, api_client, detail_url, payload, document_source
    ):
        response = api_client.patch(detail_url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetDocumentSourceViewDelete:
    def test_user_with_delete_permission_can_delete_source(
        self, api_client_with_change_permission, detail_url, document_source
    ):
        source_id = document_source.id

        response = api_client_with_change_permission.delete(detail_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DocumentSource.objects.filter(id=source_id).exists()

    def test_user_without_delete_permission_cannot_delete_source(self, api_client, detail_url, document_source):
        source_id = document_source.id

        response = api_client.delete(detail_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert DocumentSource.objects.filter(id=source_id).exists()
