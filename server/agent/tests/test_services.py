from unittest.mock import Mock, patch

import pytest
from enthusiast_common.config import FunctionToolConfig
from enthusiast_common.tools import BaseFunctionTool
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field

from agent.models import Agent
from agent.services import AgentService
from catalog.models import DataSet

pytestmark = pytest.mark.django_db


class ToolArgs(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")
    without_default: str = Field(description="description", title="title")


class DummyTool(BaseFunctionTool):
    CONFIGURATION_ARGS = ToolArgs


class AgentArgs(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")
    without_default: str = Field(description="description", title="title")


class PromptInput(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")
    without_default: str = Field(description="description", title="title")


class PromptExtension(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")
    without_default: str = Field(description="description", title="title")


class MockAgentClass:
    AGENT_ARGS = AgentArgs
    PROMPT_INPUT = PromptInput
    PROMPT_EXTENSION = PromptExtension
    TOOLS = [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool)]
    FILE_UPLOAD = False


EXPECTED_AGENT_CONFIG = {
    'agent_args': {'with_default': 'default'},
    'prompt_extension': {'with_default': 'default'},
    'prompt_input': {'with_default': 'default'},
    'tools': [{'with_default': 'default'}, {'with_default': 'default'}]
}


@pytest.fixture(autouse=True)
def django_settings(settings):
    settings.AVAILABLE_AGENTS = {
        "dummy_agent": {
            "name": "Dummy Agent",
            "agent_directory_path": "dummy_agent_directory_path",
        }
    }


class TestAgentService:

    @pytest.fixture
    def dataset(self):
        return DataSet.objects.create(name="Test Dataset")

    @patch("agent.services.AgentRegistry")
    def test_preconfigure_available_agents_creates_agents(
            self,
            mock_agent_registry,
            dataset
    ):
        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = MockAgentClass
        mock_agent_registry.return_value = mock_registry_instance

        AgentService.preconfigure_available_agents(dataset)

        qs = Agent.objects.filter(dataset=dataset)
        assert Agent.objects.filter(dataset=dataset).exists()
        assert qs.first().config == EXPECTED_AGENT_CONFIG

    @patch("agent.services.AgentRegistry")
    def test_preconfigure_available_agents_skips_existing_agent(
            self,
            mock_agent_registry,
            dataset
    ):
        Agent.objects.create(
            name="Existing Dummy Agent",
            description="Existing",
            config={"foo": "bar"},
            dataset=dataset,
            agent_type="dummy_agent"
        )

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = MockAgentClass
        mock_agent_registry.return_value = mock_registry_instance

        AgentService.preconfigure_available_agents(dataset)

        assert Agent.objects.filter(dataset=dataset, agent_type="dummy_agent").count() == 1
        mock_registry_instance.get_agent_class_by_type.assert_not_called()
