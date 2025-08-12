from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from enthusiast_common.config import FunctionToolConfig
from enthusiast_common.tools import BaseFunctionTool
from enthusiast_common.utils import RequiredFieldsModel
from model_bakery import baker
from pydantic import Field
from rest_framework import status
from rest_framework.test import APIClient

from account.models import User
from agent.models import Conversation
from agent.models.agent import Agent
from catalog.models import DataSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return baker.make(User)


@pytest.fixture
def dataset(user):
    return baker.make(DataSet, users=[user])


@pytest.fixture
def agent(dataset):
    return baker.make(Agent, deleted_at=None, dataset=dataset)


@pytest.fixture
def deleted_agent(dataset):
    return baker.make(Agent, deleted_at=timezone.now(), dataset=dataset)


@pytest.fixture
def conversation(user, agent, dataset):
    return baker.make(Conversation, user=user, agent=agent, data_set=dataset)


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class ToolArgs(RequiredFieldsModel):
    required_test: str = Field(description="description", title="title")
    optional_test: str = Field(description="description", title="title", default="default")


class DummyTool(BaseFunctionTool):
    CONFIGURATION_ARGS = ToolArgs


class AgentArgs(RequiredFieldsModel):
    required_test: str = Field(description="description", title="title")
    optional_test: str = Field(description="description", title="title", default="default")


class PromptInput(RequiredFieldsModel):
    required_test: str = Field(description="description", title="title")
    optional_test: str = Field(description="description", title="title", default="default")


class PromptExtension(RequiredFieldsModel):
    required_test: str = Field(description="description", title="title")
    optional_test: str = Field(description="description", title="title", default="default")


class DummyAgent:
    AGENT_ARGS = AgentArgs
    PROMPT_INPUT = PromptInput
    PROMPT_EXTENSION = PromptExtension
    TOOLS = [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool)]


@pytest.fixture(autouse=True)
def django_settings(settings):
    settings.AVAILABLE_AGENTS = {
        "agent_1": {
            "name": "Agent 1",
            "agent": "agent_path_1",
            "config": "config_path_1",
            "builder": "builder_path_1",
        },
        "agent_2": {
            "name": "Agent 2",
            "agent": "agent_path_2",
            "config": "config_path_2",
            "builder": "builder_path_2",
        },
    }


@pytest.fixture
def config():
    return {
        "agent_args": {
            "required_test": "required_test",
            "optional_test": "optional_test",
        },
        "prompt_input": {
            "required_test": "required_test",
            "optional_test": "optional_test",
        },
        "prompt_extension": {
            "required_test": "required_test",
            "optional_test": "optional_test",
        },
        "tools": [
            {"required_test": "required_test", "optional_test": "optional_test"},
            {"required_test": "required_test", "optional_test": "optional_test"},
        ],
    }


class TestAgentTypesView:
    def test_get_agent_types_returns_200(self, api_client):
        url = reverse("agent-types")
        with patch("agent.views.AgentRegistry.get_agent_class_by_type", return_value=DummyAgent):
            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["choices"]) == 2
            assert response.data["choices"][0]["key"] == "agent_1"
            assert response.data["choices"][1]["key"] == "agent_2"
            assert len(response.data["choices"][0]["tools"]) == 2
            assert len(response.data["choices"][1]["tools"]) == 2
            assert list(response.data["choices"][0]["tools"][0].keys()) == ["required_test", "optional_test"]

    def test_get_agent_types_returns_401(self):
        response = APIClient().get(reverse("agent-types"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAgentView:
    @pytest.fixture
    def url(self):
        return reverse("agents")

    @pytest.fixture
    def dataset_instance(self):
        return baker.make(DataSet)

    def test_get_empty_list(self, api_client, url, dataset_instance):
        response = api_client.get(f"{url}?dataset={dataset_instance.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_get_multiple_agents(self, api_client, url, dataset_instance):
        config_1 = baker.make(Agent, name="cfg1", config={"a": 1}, dataset=dataset_instance)
        config_2 = baker.make(Agent, name="cfg2", config={"b": 2}, dataset=dataset_instance)

        response = api_client.get(f"{url}?dataset={dataset_instance.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        ids = {item["id"] for item in response.data}
        assert config_1.id in ids
        assert config_2.id in ids

    def test_get_returns_ordered_by_created_at(self, api_client, url, dataset_instance):
        older = baker.make(Agent, name="older", dataset=dataset_instance)
        newer = baker.make(Agent, name="newer", dataset=dataset_instance)

        response = api_client.get(f"{url}?dataset={dataset_instance.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["id"] == older.id
        assert response.data[1]["id"] == newer.id

    def test_get_returns_corrupted_agents_to_admin(self, user, api_client, url, dataset_instance):
        user.is_staff = True
        user.save()
        agent_1 = baker.make(Agent, dataset=dataset_instance)
        agent_2 = baker.make(Agent, dataset=dataset_instance, corrupted=True)

        response = api_client.get(f"{url}?dataset={dataset_instance.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        ids = {item["id"] for item in response.data}
        assert agent_1.id in ids
        assert agent_2.id in ids

    def test_get_filter_out_corrupted_agents_to_user(self, api_client, url, dataset_instance):
        agent_1 = baker.make(Agent, dataset=dataset_instance)
        agent_2 = baker.make(Agent, dataset=dataset_instance, corrupted=True)

        response = api_client.get(f"{url}?dataset={dataset_instance.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        ids = {item["id"] for item in response.data}
        assert agent_1.id in ids
        assert agent_2.id not in ids

    def test_dataset_not_found(self, api_client, url):
        response = api_client.get(f"{url}?dataset=9999")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_post_creates_agent(self, api_client, url, config):
        dataset = baker.make(DataSet)
        config = {
            "agent_args": {
                "required_test": "required_test",
            },
            "prompt_input": {
                "required_test": "required_test",
            },
            "prompt_extension": {
                "required_test": "required_test",
            },
            "tools": [
                {
                    "required_test": "required_test",
                },
                {
                    "required_test": "required_test",
                },
            ],
        }
        payload = {"name": "name", "config": config, "dataset": dataset.id, "agent_type": "agent_1"}

        with patch(
            "agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type",
            side_effect=[DummyAgent, DummyAgent, DummyAgent, DummyAgent],
        ):
            response = api_client.post(url, payload, format="json")

            assert response.status_code == status.HTTP_201_CREATED
            created = Agent.objects.get(pk=response.data["id"])
            assert created.name == "name"

    def test_post_creates_agent_optional_fields_saved(self, api_client, url, config):
        dataset = baker.make(DataSet)
        config = {
            "agent_args": {
                "required_test": "required_test",
                "optional_test": "optional_test",
            },
            "prompt_input": {
                "required_test": "required_test",
                "optional_test": "optional_test",
            },
            "prompt_extension": {
                "required_test": "required_test",
                "optional_test": "optional_test",
            },
            "tools": [
                {"required_test": "required_test", "optional_test": "optional_test"},
                {"required_test": "required_test", "optional_test": "optional_test"},
            ],
        }
        payload = {"name": "name", "config": config, "dataset": dataset.id, "agent_type": "agent_1"}

        with patch(
            "agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type",
            side_effect=[DummyAgent, DummyAgent, DummyAgent, DummyAgent],
        ):
            response = api_client.post(url, payload, format="json")

            assert response.status_code == status.HTTP_201_CREATED
            created = Agent.objects.get(pk=response.data["id"])
            assert created.name == "name"
            assert created.config["tools"][0].get("optional_test") == "optional_test"
            assert created.config["tools"][1].get("optional_test") == "optional_test"
            assert created.config["agent_args"].get("optional_test") == "optional_test"
            assert created.config["prompt_input"].get("optional_test") == "optional_test"
            assert created.config["prompt_extension"].get("optional_test") == "optional_test"

    def test_post_creates_agent_do_not_save_empty_field(self, api_client, url, config):
        dataset = baker.make(DataSet)
        config = {
            "agent_args": {
                "required_test": "required_test",
            },
            "prompt_input": {
                "required_test": "required_test",
            },
            "prompt_extension": {
                "required_test": "required_test",
            },
            "tools": [{"required_test": "required_test"}, {"required_test": "required_test"}],
        }
        payload = {"name": "name", "config": config, "dataset": dataset.id, "agent_type": "agent_1"}

        class NoArgsDummyTool(BaseFunctionTool):
            CONFIGURATION_ARGS = None

        class NoArgsDummyAgent:
            AGENT_ARGS = None
            PROMPT_INPUT = PromptInput
            PROMPT_EXTENSION = PromptExtension
            TOOLS = [FunctionToolConfig(tool_class=NoArgsDummyTool), FunctionToolConfig(tool_class=DummyTool)]

        with patch(
            "agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type",
            side_effect=[NoArgsDummyAgent, NoArgsDummyAgent, NoArgsDummyAgent, NoArgsDummyAgent],
        ):
            response = api_client.post(url, payload, format="json")

            assert response.status_code == status.HTTP_201_CREATED
            created = Agent.objects.get(pk=response.data["id"])
            assert created.name == "name"
            assert created.config["agent_args"] == {}
            assert created.config["tools"][0] == {}
            assert created.config["tools"][1] == {"required_test": "required_test", "optional_test": "default"}


class TestAgentDetailsView:
    @pytest.fixture
    def agent_instance(self, config):
        return baker.make(Agent, name="cfg1", config=config)

    @pytest.fixture
    def url(self, agent_instance):
        return reverse("agent-details", kwargs={"pk": agent_instance.pk})

    def test_get_existing_agent(self, api_client, agent_instance, url):
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == agent_instance.name
        assert response.data["config"]

    def test_get_nonexistent_agent_returns_404(self, api_client):
        url = reverse("agent-details", kwargs={"pk": 9999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_updates_agent(self, api_client, agent_instance, url, config):
        dataset = baker.make(DataSet)
        updated_config = {
            "agent_args": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "prompt_input": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "prompt_extension": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "tools": [
                {"required_test": "required_upated", "optional_test": "optional_updated"},
                {"required_test": "required_updated", "optional_test": "optional_updated"},
            ],
        }
        payload = {"name": "updated", "config": updated_config, "dataset": dataset.id, "agent_type": "agent_1"}
        with patch(
            "agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type",
            side_effect=[DummyAgent, DummyAgent, DummyAgent, DummyAgent],
        ):
            response = api_client.put(url, payload, format="json")

            assert response.status_code == status.HTTP_200_OK
            agent_instance.refresh_from_db()
            assert agent_instance.name == "updated"
            assert agent_instance.config == updated_config

    def test_put_removes_corrupted_flag_for_correct_data(self, api_client, url, config):
        dataset = baker.make(DataSet)
        agent_instance = baker.make(Agent, corrupted=True, deleted_at=None, dataset=dataset)
        url = reverse("agent-details", kwargs={"pk": agent_instance.pk})
        updated_config = {
            "agent_args": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "prompt_input": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "prompt_extension": {
                "required_test": "required_updated",
                "optional_test": "optional_updated",
            },
            "tools": [
                {"required_test": "required_upated", "optional_test": "optional_updated"},
                {"required_test": "required_updated", "optional_test": "optional_updated"},
            ],
        }
        payload = {"name": "updated", "config": updated_config, "dataset": dataset.id, "agent_type": "agent_1"}
        with patch(
            "agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type",
            side_effect=[DummyAgent, DummyAgent, DummyAgent, DummyAgent],
        ):
            response = api_client.put(url, payload, format="json")

            assert response.status_code == status.HTTP_200_OK
            agent_instance.refresh_from_db()
            assert agent_instance.corrupted is False

    def test_put_nonexistent_returns_404(self, api_client):
        url = reverse("agent-details", kwargs={"pk": 9999})
        payload = {"name": "anything", "config": {"x": "y"}}

        response = api_client.put(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_put_invalid_payload_returns_400(self, api_client, url):
        payload = {"name": ""}

        response = api_client.put(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "config" in response.data

    def test_delete_existing_agent(self, api_client, agent_instance, url):
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        agent_instance = Agent.all_objects.get(pk=agent_instance.pk)
        assert agent_instance.deleted_at is not None

    def test_delete_nonexistent_agent_returns_404(self, api_client, url):
        url = reverse("agent-details", kwargs={"pk": 9999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConversationView:
    @pytest.fixture
    def url(self, conversation):
        return reverse("conversation-details", kwargs={"conversation_id": conversation.id})

    def test_valid_post_returns_202(self, api_client, url, conversation):
        payload = {
            "data_set_id": conversation.data_set.id,
            "question_message": "Hello?",
            "streaming": True,
        }
        with (
            patch(
                "agent.views.respond_to_user_message_task.apply_async",
                return_value=type("obj", (), {"id": "fake-task-id"}),
            ) as mock_task,
            patch("agent.views.LanguageModelRegistry.provider_for_dataset") as mock_provider,
        ):
            mock_provider.return_value = type("obj", (), {"STREAMING_AVAILABLE": True})
            response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["task_id"] == "fake-task-id"
        assert response.data["streaming"] is True
        mock_task.assert_called_once()

    def test_invalid_payload_returns_400(self, api_client, url):
        payload = {"data_set_id": None}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "question_message" in response.data

    def test_agent_soft_deleted_returns_400(self, api_client, conversation, url):
        conversation.agent.deleted_at = timezone.now()
        conversation.agent.save()

        payload = {
            "data_set_id": conversation.data_set.id,
            "question_message": "Hello?",
            "streaming": False,
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Conversation locked."

    def test_conversation_not_found_returns_404(self, api_client):
        url = reverse("conversation-details", kwargs={"conversation_id": 99999})
        payload = {
            "data_set_id": 1,
            "question_message": "Hello?",
            "streaming": False,
        }
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestConversationListView:
    def test_create_conversation_success(self, api_client, agent):
        url = reverse("conversation-list")
        payload = {"agent_id": agent.id}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["agent"]["id"] == agent.id

    def test_create_conversation_invalid_payload(self, api_client):
        url = reverse("conversation-list")
        payload = {"wrong_field": 123}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "agent_id" in response.data

    def test_create_conversation_with_deleted_agent(self, api_client, deleted_agent):
        url = reverse("conversation-list")
        payload = {"agent_id": deleted_agent.id}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
