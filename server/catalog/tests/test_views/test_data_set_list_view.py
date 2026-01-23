from unittest.mock import Mock, patch

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from agent.models import Agent
from catalog.models import DataSet

pytestmark = pytest.mark.django_db

class MockAgentClass:
    AGENT_ARGS = type("AgentArgs", (), {"model_fields": {}})
    PROMPT_INPUT = type("PromptInput", (), {"model_fields": {}})
    PROMPT_EXTENSION = type("PromptExtension", (), {"model_fields": {}})
    TOOLS = []
    FILE_UPLOAD = False

@pytest.mark.django_db
class TestDataSetListViewPost:
    MOCK_AGENT_CLASS = MockAgentClass

    @pytest.fixture
    def url(self):
        return reverse("data_set_list")

    @pytest.fixture
    def payload(self):
        return {"name": "New DataSet"}

    @pytest.fixture
    def payload_preconfigure_agents(self):
        return {"name": "New DataSet", "preconfigure_agents": True}

    def test_staff_can_create_dataset(self, admin_api_client, url, payload):
        response = admin_api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert DataSet.objects.filter(name="New DataSet").exists()

    def test_non_staff_cannot_create_dataset(self, api_client, url, payload):
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not DataSet.objects.filter(name="New DataSet").exists()

    def test_staff_dataset_creation_with_no_agent_preconfiguration(self, admin_api_client, url, payload):
        response = admin_api_client.post(url, payload, format="json")

        dataset = DataSet.objects.get(name="New DataSet")
        assert response.status_code == status.HTTP_201_CREATED
        assert not Agent.objects.filter(dataset=dataset).exists()

    @patch('agent.services.AgentRegistry')
    @override_settings(
        AVAILABLE_AGENTS={
            "dummy_agent": {
                "name": "Dummy Agent",
                "agent_directory_path": "dummy_agent_directory_path",
            }
        })
    def test_staff_dataset_creation_with_agent_preconfiguration(self,
                                                                mock_agent_registry,
                                                                admin_api_client,
                                                                url,
                                                                payload_preconfigure_agents):
        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance
        response = admin_api_client.post(url, payload_preconfigure_agents, format="json")

        dataset = DataSet.objects.get(name="New DataSet")
        assert response.status_code == status.HTTP_201_CREATED
        mock_registry_instance.get_agent_class_by_type.assert_called()

        assert Agent.objects.filter(dataset=dataset).exists()

