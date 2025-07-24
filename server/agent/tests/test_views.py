import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from agent.models.agent_config import AgentConfiguration
from catalog.models import DataSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def config():
    return {
        "prompt_template": "prompt_template",
        "agent_class": "agent_class",
        "llm": {"llm_class": "llm_class", "callbacks": ["callbacks"], "streaming": True},
        "repositories": {
            "user": "user",
            "message": "message",
            "conversation": "conversation",
            "data_set": "data_set",
            "document_chunk": "document_chunk",
            "product": "product",
            "product_chunk": "product_chunk",
        },
        "retrievers": {
            "document": {"retriever_class": "retriever_class", "extra_kwargs": {"top_k": "5"}},
            "product": {"retriever_class": "retriever_class", "extra_kwargs": {"filter": "available"}},
        },
        "injector": "injector",
        "registry": {
            "llm": {"registry_class": "registry_class", "providers": {"openai": "openai"}},
            "embeddings": {"registry_class": "registry_class", "providers": {"openai": "openai"}},
            "model": {
                "registry_class": "registry_class",
                "models_config": {
                    "my_model": "my_model",
                },
            },
        },
        "function_tools": ["FunctionTool"],
        "llm_tools": [{"tool_class": "tool_class", "llm": "llm"}],
        "agent_tools": [{"tool_class": "tool_class", "agent": "agent"}],
        "agent_callback_handler": {"handler_class": "handler_class", "args": {"log_level": "debug"}},
    }


class TestConfigOptionsView:
    def test_get_config_options_returns_200(self, api_client):
        url = reverse("config-options")

        response = api_client.get(url)

        assert response.status_code == 200
        assert isinstance(response.data, dict)
        for key in [
            "agents",
            "prompt_templates",
            "llm",
            "llm_callback_handlers",
            "agent_callback_handlers",
            "repositories",
            "retrievers",
            "injectors",
            "registries",
            "tools",
        ]:
            assert key in response.data


class TestConfigView:
    @pytest.fixture
    def url(self):
        return reverse("configs")

    def test_get_empty_list(self, api_client, url):
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data == []

    def test_get_multiple_configurations(self, api_client, url):
        config_1 = baker.make(AgentConfiguration, name="cfg1", config={"a": 1})
        config_2 = baker.make(AgentConfiguration, name="cfg2", config={"b": 2})

        response = api_client.get(url)

        assert response.status_code == 200
        ids = {item["id"] for item in response.data}
        assert config_1.id in ids
        assert config_2.id in ids

    def test_get_returns_ordered_by_created_at(self, api_client, url):
        older = baker.make(AgentConfiguration, name="older")
        newer = baker.make(AgentConfiguration, name="newer")

        response = api_client.get(url)

        assert response.status_code == 200
        response.data[0]["id"] = older.id
        response.data[1]["id"] = newer.id

    def test_post_creates_configuration(self, api_client, url, config):
        dataset = baker.make(DataSet)
        payload = {"name": "name", "config": config, "dataset": dataset.id}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 201
        created = AgentConfiguration.objects.get(pk=response.data["id"])
        assert created.name == "name"

    def test_post_missing_required_name(self, api_client, url):
        payload = {"config": {"foo": "bar"}}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 400
        assert "name" in response.data

    def test_post_missing_config_field(self, api_client, url):
        payload = {"name": "cfg_without_config"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 400
        assert "config" in response.data


class TestConfigDetailsView:
    @pytest.fixture
    def config_instance(self, config):
        return baker.make(AgentConfiguration, name="cfg1", config=config)

    @pytest.fixture
    def url(self, config_instance):
        return reverse("config-details", kwargs={"pk": config_instance.pk})

    def test_get_existing_configuration(self, api_client, config_instance, url):
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["name"] == config_instance.name
        assert response.data["config"]

    def test_get_nonexistent_configuration_returns_404(self, api_client):
        url = reverse("config-details", kwargs={"pk": 9999})

        response = api_client.get(url)

        assert response.status_code == 404

    def test_put_updates_configuration(self, api_client, config_instance, url, config):
        config["name"] = "updated"
        dataset = baker.make(DataSet)
        payload = {"name": "updated", "config": config, "dataset": dataset.id}

        response = api_client.put(url, payload, format="json")

        assert response.status_code == 200
        config_instance.refresh_from_db()
        assert config_instance.name == "updated"

    def test_put_nonexistent_returns_404(self, api_client):
        url = reverse("config-details", kwargs={"pk": 9999})
        payload = {"name": "anything", "config": {"x": "y"}}

        response = api_client.put(url, payload, format="json")

        assert response.status_code == 404

    def test_put_invalid_payload_returns_400(self, api_client, url):
        payload = {"name": ""}

        response = api_client.put(url, payload, format="json")

        assert response.status_code == 400
        assert "config" in response.data

    def test_delete_existing_configuration(self, api_client, config_instance, url):
        response = api_client.delete(url)

        assert response.status_code == 204
        assert not AgentConfiguration.objects.filter(pk=config_instance.pk).exists()

    def test_delete_nonexistent_configuration_returns_404(self, api_client, url):
        url = reverse("config-details", kwargs={"pk": 9999})
        response = api_client.delete(url)
        assert response.status_code == 404
