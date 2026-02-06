from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import DataSet, Document, DocumentSource, Product, ProductSource

pytestmark = pytest.mark.django_db


@pytest.fixture
def limited_admin_with_dataset(limited_admin_user):
    data_set = baker.make(DataSet)
    data_set.users.add(limited_admin_user)
    return limited_admin_user, data_set


@pytest.fixture
def limited_admin_with_dataset_client(limited_admin_with_dataset):
    user, _ = limited_admin_with_dataset
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestDataSetDetailView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_detail", kwargs={"data_set_id": data_set.id})

    def test_full_admin_can_view_any_dataset(self, admin_api_client, url, data_set):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == data_set.id

    def test_limited_admin_can_view_their_dataset(self, limited_admin_with_dataset_client, limited_admin_with_dataset):
        _, data_set = limited_admin_with_dataset
        url = reverse("data_set_detail", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == data_set.id

    def test_limited_admin_cannot_view_other_dataset(self, limited_admin_api_client, data_set):
        url = reverse("data_set_detail", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_view_dataset(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetListView:
    @pytest.fixture
    def url(self):
        return reverse("data_set_list")

    def test_full_admin_sees_all_datasets(self, admin_api_client, url):
        dataset1 = baker.make(DataSet, name="Dataset 1")
        dataset2 = baker.make(DataSet, name="Dataset 2")

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        dataset_names = [ds["name"] for ds in response.data["results"]]
        assert dataset1.name in dataset_names
        assert dataset2.name in dataset_names

    def test_limited_admin_sees_only_their_datasets(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        user, their_dataset = limited_admin_with_dataset
        other_dataset = baker.make(DataSet, name="Other Dataset")
        url = reverse("data_set_list")

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        dataset_ids = [ds["id"] for ds in response.data["results"]]
        assert their_dataset.id in dataset_ids
        assert other_dataset.id not in dataset_ids

    def test_regular_user_sees_only_their_datasets(self, api_client, url, user):
        their_dataset = baker.make(DataSet, name="Their Dataset")
        their_dataset.users.add(user)
        other_dataset = baker.make(DataSet, name="Other Dataset")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        dataset_ids = [ds["id"] for ds in response.data["results"]]
        assert their_dataset.id in dataset_ids
        assert other_dataset.id not in dataset_ids

    def test_limited_admin_can_create_dataset(self, limited_admin_api_client, url):
        payload = {"name": "New Dataset"}

        response = limited_admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DataSet.objects.filter(name="New Dataset").exists()


class TestDataSetUserListView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_user_list", kwargs={"data_set_id": data_set.id})

    def test_full_admin_can_list_dataset_users(self, admin_api_client, url, data_set, user):
        data_set.users.add(user)

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_full_admin_can_add_user_to_dataset(self, admin_api_client, url, data_set, user):
        payload = {"user_id": user.id}

        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert user in data_set.users.all()

    def test_limited_admin_cannot_list_dataset_users(self, limited_admin_api_client, url):
        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_limited_admin_cannot_add_user_to_dataset(self, limited_admin_api_client, url, data_set, user):
        payload = {"user_id": user.id}

        response = limited_admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert user not in data_set.users.all()


class TestDataSetUserView:
    @pytest.fixture
    def url(self, data_set, user):
        data_set.users.add(user)
        return reverse("data_set_user_details", kwargs={"data_set_id": data_set.id, "user_id": user.id})

    def test_full_admin_can_remove_user_from_dataset(self, admin_api_client, url, data_set, user):
        response = admin_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert user not in data_set.users.all()

    def test_limited_admin_cannot_remove_user_from_dataset(self, limited_admin_api_client, url):
        response = limited_admin_api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetProductSourceListView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_product_source_list", kwargs={"data_set_id": data_set.id})

    def test_limited_admin_can_list_product_sources_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        baker.make(ProductSource, data_set=data_set, _quantity=2)
        url = reverse("data_set_product_source_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_cannot_list_product_sources_in_other_dataset(self, limited_admin_api_client, data_set):
        baker.make(ProductSource, data_set=data_set, _quantity=2)
        url = reverse("data_set_product_source_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_regular_user_cannot_list_product_sources(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("catalog.views.sync_product_source")
    def test_limited_admin_can_create_product_source_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        mock_task.apply_async.return_value = Mock(id="test-id")
        _, data_set = limited_admin_with_dataset
        url = reverse("data_set_product_source_list", kwargs={"data_set_id": data_set.id})
        payload = {"plugin_name": "Test Plugin", "config": {}}

        response = limited_admin_with_dataset_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert ProductSource.objects.filter(plugin_name="Test Plugin", data_set=data_set).exists()
        mock_task.apply_async.assert_called_once()


class TestDataSetProductSourceView:
    @pytest.fixture
    def url(self, data_set, product_source):
        return reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

    def test_full_admin_can_view_product_source(self, admin_api_client, url, product_source):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product_source.id

    def test_limited_admin_can_view_product_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        product_source = baker.make(ProductSource, data_set=data_set)
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product_source.id

    def test_limited_admin_cannot_view_product_source_in_other_dataset(
        self, limited_admin_api_client, data_set, product_source
    ):
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_view_product_source(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_full_admin_can_update_product_source(self, admin_api_client, url, product_source):
        payload = {"plugin_name": "Updated Plugin"}

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        product_source.refresh_from_db()
        assert product_source.plugin_name == "Updated Plugin"

    def test_limited_admin_can_update_product_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        product_source = baker.make(ProductSource, data_set=data_set, plugin_name="Original")
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )
        payload = {"plugin_name": "Updated Plugin"}

        response = limited_admin_with_dataset_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        product_source.refresh_from_db()
        assert product_source.plugin_name == "Updated Plugin"

    def test_limited_admin_cannot_update_product_source_in_other_dataset(
        self, limited_admin_api_client, data_set, product_source
    ):
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )
        payload = {"plugin_name": "Updated Plugin"}

        response = limited_admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_full_admin_can_delete_product_source(self, admin_api_client, url, product_source):
        product_source_id = product_source.id

        response = admin_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProductSource.objects.filter(id=product_source_id).exists()

    def test_limited_admin_can_delete_product_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        product_source = baker.make(ProductSource, data_set=data_set)
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )
        product_source_id = product_source.id

        response = limited_admin_with_dataset_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProductSource.objects.filter(id=product_source_id).exists()

    def test_limited_admin_cannot_delete_product_source_in_other_dataset(
        self, limited_admin_api_client, data_set, product_source
    ):
        url = reverse(
            "data_set_product_source_details",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )
        product_source_id = product_source.id

        response = limited_admin_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ProductSource.objects.filter(id=product_source_id).exists()


class TestDataSetDocumentSourceListView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})

    def test_limited_admin_can_list_document_sources_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        baker.make(DocumentSource, data_set=data_set, _quantity=2)
        url = reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_cannot_list_document_sources_in_other_dataset(self, limited_admin_api_client, data_set):
        baker.make(DocumentSource, data_set=data_set, _quantity=2)
        url = reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_regular_user_cannot_list_document_sources(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("catalog.views.sync_document_source")
    def test_limited_admin_can_create_document_source_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        mock_task.apply_async.return_value = Mock(id="test-id")
        _, data_set = limited_admin_with_dataset
        url = reverse("data_set_document_source_list", kwargs={"data_set_id": data_set.id})
        payload = {"plugin_name": "Test Plugin", "config": {}}

        response = limited_admin_with_dataset_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DocumentSource.objects.filter(plugin_name="Test Plugin", data_set=data_set).exists()
        mock_task.apply_async.assert_called_once()


class TestDataSetDocumentSourceView:
    @pytest.fixture
    def url(self, data_set, document_source):
        return reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

    def test_full_admin_can_view_document_source(self, admin_api_client, url, document_source):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == document_source.id

    def test_limited_admin_can_view_document_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        document_source = baker.make(DocumentSource, data_set=data_set)
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == document_source.id

    def test_limited_admin_cannot_view_document_source_in_other_dataset(
        self, limited_admin_api_client, data_set, document_source
    ):
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_view_document_source(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_full_admin_can_update_document_source(self, admin_api_client, url, document_source):
        payload = {"plugin_name": "Updated Plugin"}

        response = admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        document_source.refresh_from_db()
        assert document_source.plugin_name == "Updated Plugin"

    def test_limited_admin_can_update_document_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        document_source = baker.make(DocumentSource, data_set=data_set, plugin_name="Original")
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )
        payload = {"plugin_name": "Updated Plugin"}

        response = limited_admin_with_dataset_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        document_source.refresh_from_db()
        assert document_source.plugin_name == "Updated Plugin"

    def test_limited_admin_cannot_update_document_source_in_other_dataset(
        self, limited_admin_api_client, data_set, document_source
    ):
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )
        payload = {"plugin_name": "Updated Plugin"}

        response = limited_admin_api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_full_admin_can_delete_document_source(self, admin_api_client, url, document_source):
        document_source_id = document_source.id

        response = admin_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DocumentSource.objects.filter(id=document_source_id).exists()

    def test_limited_admin_can_delete_document_source_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        document_source = baker.make(DocumentSource, data_set=data_set)
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )
        document_source_id = document_source.id

        response = limited_admin_with_dataset_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DocumentSource.objects.filter(id=document_source_id).exists()

    def test_limited_admin_cannot_delete_document_source_in_other_dataset(
        self, limited_admin_api_client, data_set, document_source
    ):
        url = reverse(
            "data_set_document_source_details",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )
        document_source_id = document_source.id

        response = limited_admin_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert DocumentSource.objects.filter(id=document_source_id).exists()


class TestProductListView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_product_list", kwargs={"data_set_id": data_set.id})

    def test_full_admin_can_view_products_in_any_dataset(self, admin_api_client, url, data_set):
        baker.make(Product, data_set=data_set, _quantity=2)

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_can_view_products_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        baker.make(Product, data_set=data_set, _quantity=2)
        url = reverse("data_set_product_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_cannot_view_products_in_other_dataset(self, limited_admin_api_client):
        data_set = baker.make(DataSet)
        url = reverse("data_set_product_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDocumentListView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_document_list", kwargs={"data_set_id": data_set.id})

    def test_full_admin_can_view_documents_in_any_dataset(self, admin_api_client, url, data_set):
        baker.make(Document, data_set=data_set, _quantity=2)

        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_can_view_documents_in_their_dataset(
        self, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        baker.make(Document, data_set=data_set, _quantity=2)
        url = reverse("data_set_document_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_limited_admin_cannot_view_documents_in_other_dataset(self, limited_admin_api_client, data_set):
        url = reverse("data_set_document_list", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSyncAllSourcesView:
    @pytest.fixture
    def url(self):
        return reverse("all_sources_sync")

    def test_full_admin_can_sync_all_sources(self, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data

    def test_limited_admin_cannot_sync_all_sources(self, limited_admin_api_client, url):
        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_regular_user_cannot_sync_all_sources(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncDataSetAllSourcesView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_all_sources_sync", kwargs={"data_set_id": data_set.id})

    def test_full_admin_can_sync_dataset_sources(self, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data

    def test_limited_admin_cannot_sync_dataset_sources(self, limited_admin_api_client, url):
        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncAllProductSourcesView:
    @pytest.fixture
    def url(self):
        return reverse("all_product_sources_sync")

    def test_full_admin_can_sync_all_product_sources(self, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data

    def test_limited_admin_cannot_sync_all_product_sources(self, limited_admin_api_client, url):
        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncAllDocumentSourcesView:
    @pytest.fixture
    def url(self):
        return reverse("all_document_sources_sync")

    def test_full_admin_can_sync_all_document_sources(self, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data

    def test_limited_admin_cannot_sync_all_document_sources(self, limited_admin_api_client, url):
        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncDataSetProductSourcesView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_product_sources_sync", kwargs={"data_set_id": data_set.id})

    @patch("catalog.views.sync_data_set_product_sources.apply_async")
    def test_full_admin_can_sync_product_sources(self, mock_task, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once()

    @patch("catalog.views.sync_data_set_product_sources.apply_async")
    def test_limited_admin_can_sync_product_sources_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        url = reverse("data_set_product_sources_sync", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[data_set.id])

    def test_limited_admin_cannot_sync_product_sources_in_other_dataset(self, limited_admin_api_client, data_set):
        url = reverse("data_set_product_sources_sync", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_sync_product_sources(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncDataSetProductSourceView:
    @pytest.fixture
    def url(self, data_set, product_source):
        return reverse(
            "data_set_product_source_sync",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

    @patch("catalog.views.sync_product_source.apply_async")
    def test_full_admin_can_sync_product_source(self, mock_task, admin_api_client, url, product_source):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[product_source.id])

    @patch("catalog.views.sync_product_source.apply_async")
    def test_limited_admin_can_sync_product_source_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        product_source = baker.make(ProductSource, data_set=data_set)
        url = reverse(
            "data_set_product_source_sync",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

        response = limited_admin_with_dataset_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[product_source.id])

    def test_limited_admin_cannot_sync_product_source_in_other_dataset(self, limited_admin_api_client, data_set):
        product_source = baker.make(ProductSource, data_set=data_set)
        url = reverse(
            "data_set_product_source_sync",
            kwargs={"data_set_id": data_set.id, "product_source_id": product_source.id},
        )

        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_sync_product_source(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncDataSetDocumentSourcesView:
    @pytest.fixture
    def url(self, data_set):
        return reverse("data_set_document_sources_sync", kwargs={"data_set_id": data_set.id})

    @patch("catalog.views.sync_data_set_document_sources.apply_async")
    def test_full_admin_can_sync_document_sources(self, mock_task, admin_api_client, url):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once()

    @patch("catalog.views.sync_data_set_document_sources.apply_async")
    def test_limited_admin_can_sync_document_sources_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        url = reverse("data_set_document_sources_sync", kwargs={"data_set_id": data_set.id})

        response = limited_admin_with_dataset_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[data_set.id])

    def test_limited_admin_cannot_sync_document_sources_in_other_dataset(self, limited_admin_api_client, data_set):
        url = reverse("data_set_document_sources_sync", kwargs={"data_set_id": data_set.id})

        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_sync_document_sources(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSyncDataSetDocumentSourceView:
    @pytest.fixture
    def url(self, data_set, document_source):
        return reverse(
            "data_set_document_source_sync",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

    @patch("catalog.views.sync_document_source.apply_async")
    def test_full_admin_can_sync_document_source(self, mock_task, admin_api_client, url, document_source):
        response = admin_api_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[document_source.id])

    @patch("catalog.views.sync_document_source.apply_async")
    def test_limited_admin_can_sync_document_source_in_their_dataset(
        self, mock_task, limited_admin_with_dataset_client, limited_admin_with_dataset
    ):
        _, data_set = limited_admin_with_dataset
        document_source = baker.make(DocumentSource, data_set=data_set)
        url = reverse(
            "data_set_document_source_sync",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

        response = limited_admin_with_dataset_client.post(url)

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data
        mock_task.assert_called_once_with(args=[document_source.id])

    def test_limited_admin_cannot_sync_document_source_in_other_dataset(self, limited_admin_api_client, data_set):
        document_source = baker.make(DocumentSource, data_set=data_set)
        url = reverse(
            "data_set_document_source_sync",
            kwargs={"data_set_id": data_set.id, "document_source_id": document_source.id},
        )

        response = limited_admin_api_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_regular_user_cannot_sync_document_source(self, api_client, url):
        response = api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConfigView:
    @pytest.fixture
    def url(self):
        return reverse("config")

    def test_full_admin_can_view_config(self, admin_api_client, url):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "language_model_providers" in response.data
        assert "embedding_providers" in response.data

    def test_limited_admin_can_view_config(self, limited_admin_api_client, url):
        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "language_model_providers" in response.data
        assert "embedding_providers" in response.data

    def test_regular_user_cannot_view_config(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConfigLanguageModelView:
    @pytest.fixture
    def url(self):
        return reverse("config_language_model_provider", kwargs={"provider_name": "OpenAI"})

    def test_full_admin_can_view_language_models(self, admin_api_client, url):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_limited_admin_can_view_language_models(self, limited_admin_api_client, url):
        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_regular_user_cannot_view_language_models(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConfigEmbeddingModelView:
    @pytest.fixture
    def url(self):
        return reverse("config_embedding_provider", kwargs={"provider_name": "OpenAI"})

    def test_full_admin_can_view_embedding_models(self, admin_api_client, url):
        response = admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_limited_admin_can_view_embedding_models(self, limited_admin_api_client, url):
        response = limited_admin_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_regular_user_cannot_view_embedding_models(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
