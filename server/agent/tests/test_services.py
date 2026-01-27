from unittest.mock import patch

import pytest
from enthusiast_common.config import FunctionToolConfig
from enthusiast_common.tools import BaseFunctionTool
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field

from agent.core.registries.agents.agent_registry import AgentRegistry
from agent.models import Agent
from agent.services import AgentService
from catalog.models import DataSet

pytestmark = pytest.mark.django_db


class ToolArgs(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")


class DummyTool(BaseFunctionTool):
    CONFIGURATION_ARGS = ToolArgs


class AgentArgs(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")


class AgentArgsWithoutDefaults(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")
    without_default: str = Field(description="description", title="title")


class PromptInput(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")


class PromptExtension(RequiredFieldsModel):
    with_default: str = Field(description="description", title="title", default="default")


class MockAgentClass:
    AGENT_ARGS = AgentArgs
    PROMPT_INPUT = PromptInput
    PROMPT_EXTENSION = PromptExtension
    TOOLS = [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool)]
    FILE_UPLOAD = False


class MockAgentClassFileUpload(MockAgentClass):
    FILE_UPLOAD = True


class MockAgentClassWithoutDefaults:
    AGENT_ARGS = AgentArgsWithoutDefaults
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = []
    FILE_UPLOAD = False


EXPECTED_AGENT_CONFIG = {
    "agent_args": {"with_default": "default"},
    "prompt_extension": {"with_default": "default"},
    "prompt_input": {"with_default": "default"},
    "tools": [{"with_default": "default"}, {"with_default": "default"}],
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

    @pytest.mark.parametrize(
        "agent_class, expected_file_upload_flag",
        [
            (MockAgentClass, False),
            (MockAgentClassFileUpload, True),
        ],
    )
    @patch.object(AgentRegistry, "get_agent_class_by_type")
    def test_preconfigure_available_agents_creates_agents(
        self, mock_agent_registry, agent_class, expected_file_upload_flag, dataset
    ):
        mock_agent_registry.return_value = agent_class

        AgentService.preconfigure_available_agents(dataset)

        agent = Agent.objects.filter(dataset=dataset).first()
        assert agent
        assert agent.config == EXPECTED_AGENT_CONFIG
        assert agent.file_upload is expected_file_upload_flag

    @patch.object(AgentRegistry, "get_agent_class_by_type")
    def test_preconfigure_available_agents_skip_agents_without_defaults(self, mock_agent_registry, dataset):
        mock_agent_registry.return_value = MockAgentClassWithoutDefaults

        AgentService.preconfigure_available_agents(dataset)
        assert Agent.objects.filter(dataset=dataset).count() == 0

    @patch.object(AgentRegistry, "get_agent_class_by_type")
    def test_preconfigure_available_agents_skips_existing_agent(self, mock_agent_registry, dataset):
        Agent.objects.create(
            name="Existing Dummy Agent",
            description="Existing",
            config={"foo": "bar"},
            dataset=dataset,
            agent_type="dummy_agent",
        )
        mock_agent_registry.return_value = MockAgentClass

        AgentService.preconfigure_available_agents(dataset)

        assert Agent.objects.filter(dataset=dataset, agent_type="dummy_agent").count() == 1
        mock_agent_registry.assert_not_called()
