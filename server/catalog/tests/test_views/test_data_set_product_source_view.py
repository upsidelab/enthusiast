from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from catalog.models import DataSet, ProductSource

pytestmark = pytest.mark.django_db


@pytest.fixture
def url(data_set):
    return reverse("data_set_product_source_list", kwargs={"data_set_id": data_set.id})


class TestDataSetProductSourceViewPost:
    @pytest.fixture
    def payload(self):
        return {"plugin_name": "Source 1", "config": {}}

    @patch("catalog.views.sync_product_source.apply_async")
    def test_creates_product_source_and_triggers_task(self, mock_task, admin_api_client, url, payload, data_set):
        fake_task = Mock()
        fake_task.id = "fake_id"
        mock_task.return_value = fake_task

        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        source = ProductSource.objects.get()
        assert source.plugin_name == "Source 1"
        assert source.data_set == data_set
        mock_task.assert_called_once_with(args=[source.id])

    def test_requires_admin_user(self, api_client, url, payload):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDataSetProductSourceViewGet:
    def test_get_returns_sources_for_specific_dataset(self, admin_api_client, url, data_set):
        different_data_set = baker.make(DataSet)
        baker.make(ProductSource, data_set=data_set, _quantity=3)
        baker.make(ProductSource, data_set=different_data_set, _quantity=3)

        response = admin_api_client.get(url, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        assert all(source["data_set_id"] == data_set.id for source in response.data["results"])

    def test_requires_admin_user(self, api_client, url):
        response = api_client.get(url, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
