import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from account.models import User
from agent.models import Agent
from catalog.models import DataSet

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestDataSetListViewPost:
    @pytest.fixture
    def url(self):
        return reverse("data_set_list")

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def staff_user(self):
        return baker.make(User, is_staff=True)

    @pytest.fixture
    def payload(self):
        return {"name": "New DataSet"}

    def test_staff_can_create_dataset(self, client, url, staff_user, payload):
        client.force_authenticate(staff_user)

        response = client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DataSet.objects.filter(name="New DataSet").exists()

    def test_non_staff_cannot_create_dataset(self, client, url, payload):
        user = baker.make(User, is_staff=False)
        client.force_authenticate(user)

        response = client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not DataSet.objects.filter(name="New DataSet").exists()

    def test_staff_dataset_creation_adds_default_agent(self, client, url, staff_user, payload):
        client.force_authenticate(staff_user)

        response = client.post(url, payload, format="json")

        dataset = DataSet.objects.get(name="New DataSet")
        assert response.status_code == status.HTTP_201_CREATED
        assert Agent.objects.filter(dataset=dataset).exists()

    def test_staff_dataset_creation_no_default_agent_settings(self, client, url, staff_user, payload, settings):
        settings.DEFAULT_AGENT = None
        client.force_authenticate(staff_user)

        response = client.post(url, payload, format="json")

        dataset = DataSet.objects.get(name="New DataSet")
        assert response.status_code == status.HTTP_201_CREATED
        assert not Agent.objects.filter(dataset=dataset).exists()
