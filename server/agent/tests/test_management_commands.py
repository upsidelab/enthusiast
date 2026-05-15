from typing import Any
from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command
from model_bakery import baker
from pydantic import BaseModel

from agent.core.registries.agents.agent_registry import AgentNotFoundError
from agent.models import Agent

pytestmark = pytest.mark.django_db


class MockConfigurationArgs(BaseModel):
    value_1: str
    value_2: str = "default_value"


class MockToolConfigurationArgs(BaseModel):
    tool_value_1: str
    tool_value_2: bool = True


class MockToolClass:
    NAME = "mock_tool"
    CONFIGURATION_ARGS = MockToolConfigurationArgs


class MockToolClass2:
    NAME = "mock_tool_2"
    CONFIGURATION_ARGS = MockToolConfigurationArgs


class MockToolConfig:
    def __init__(self, tool_class):
        self.tool_class = tool_class


class MockAgentClass:
    AGENT_ARGS = MockConfigurationArgs
    PROMPT_INPUT = MockConfigurationArgs
    PROMPT_EXTENSION = MockConfigurationArgs
    TOOLS = [MockToolConfig(MockToolClass), MockToolConfig(MockToolClass2)]


@pytest.fixture
def config_dict() -> dict[Any, Any]:
    return {
        "agent_args": {"value_1": "value_1", "value_2": "value_2"},
        "prompt_input": {"value_1": "value_1", "value_2": "value_2"},
        "prompt_extension": {"value_1": "value_1", "value_2": "value_2"},
        "tool_config": {
            "mock_tool": {"tool_value_1": "value_1", "tool_value_2": True},
            "mock_tool_2": {"tool_value_1": "value_1", "tool_value_2": False},
        },
    }


class TestVerifyAgentsCommand:
    AGENT_TYPE = "test_agent"
    MOCK_AGENT_CLASS = MockAgentClass

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_valid_configuration(self, mock_agent_registry, config_dict):
        valid_agent = baker.make(Agent, name="Valid Agent", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        valid_agent.refresh_from_db()
        assert valid_agent.corrupted is False

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_missing_field(self, mock_agent_registry, config_dict):
        config_dict["agent_args"] = {}
        corrupted_agent = baker.make(Agent, name="Corrupted Agent Args", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_invalid_type(self, mock_agent_registry, config_dict):
        config_dict["agent_args"]["value_1"] = 123
        corrupted_agent = baker.make(Agent, name="Corrupted Agent Args", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_missing_tool_name_in_tool_config(self, mock_agent_registry, config_dict):
        # mock_tool has valid config, but mock_tool_2 key is entirely absent
        config_dict["tool_config"] = {"mock_tool": {"tool_value_1": "value_1", "tool_value_2": True}}
        corrupted_agent = baker.make(Agent, name="Corrupted Tools", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_missing_tool_config(self, mock_agent_registry, config_dict):
        config_dict["tool_config"] = {"mock_tool": {}}
        corrupted_agent = baker.make(Agent, name="Corrupted Tools", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_invalid_tool_config_type(self, mock_agent_registry, config_dict):
        config_dict["tool_config"] = {
            "mock_tool": {"tool_value_1": "val", "tool_value_2": True},
            "mock_tool_2": {"tool_value_1": "val", "tool_value_2": "InvalidType"},
        }
        corrupted_agent = baker.make(Agent, name="Corrupted Tools", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_additional_tool(self, mock_agent_registry, config_dict):
        config_dict["tool_config"] = {}
        corrupted_agent = baker.make(Agent, name="Corrupted Tools", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_extra_tool_key_is_ignored(self, mock_agent_registry, config_dict):
        config_dict["tool_config"]["unknown_tool"] = {"tool_value_1": "value_1", "tool_value_2": True}
        valid_agent = baker.make(Agent, name="Extra Tool Key Agent", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        valid_agent.refresh_from_db()
        assert valid_agent.corrupted is False

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_missing_agent_type(self, mock_agent_registry, config_dict):
        baker.make(Agent, agent_type=self.AGENT_TYPE, config=config_dict, _quantity=3)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.side_effect = AgentNotFoundError()
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agents = Agent.objects.filter(corrupted=True)
        assert corrupted_agents.count() == 3

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_multiple_corrupted_agents(self, mock_agent_registry, config_dict):
        config_dict["tool_config"] = {"mock_tool": {}}
        baker.make(Agent, name="Corrupted Agent 1", agent_type=self.AGENT_TYPE, config=config_dict)

        baker.make(Agent, name="Corrupted Agent 2", agent_type=self.AGENT_TYPE, config=config_dict)

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agents = Agent.objects.filter(corrupted=True)
        assert corrupted_agents.count() == 2

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_agent_type_caching(self, mock_agent_registry, config_dict):
        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        baker.make(Agent, name="Another Valid Agent", agent_type=self.AGENT_TYPE, config=config_dict)

        call_command("verifyagents")

        mock_registry_instance.get_agent_class_by_type.assert_called_once_with(agent_type=self.AGENT_TYPE)

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_with_none_fields(self, mock_agent_registry):
        class MockAgentClassWithNoneFields:
            AGENT_ARGS = None
            PROMPT_INPUT = None
            PROMPT_EXTENSION = None
            TOOLS = []

        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = MockAgentClassWithNoneFields
        mock_agent_registry.return_value = mock_registry_instance

        baker.make(
            Agent,
            name="Minimal Agent",
            agent_type="minimal_agent",
            config={"agent_args": {}, "prompt_input": {}, "prompt_extension": {}, "tool_config": {}},
        )

        call_command("verifyagents")

        assert Agent.objects.filter(corrupted=True).count() == 0

    @patch("agent.management.commands.verifyagents.AgentRegistry")
    def test_verifyagents_command_non_dict_config_value(self, mock_agent_registry):
        corrupted_agent = baker.make(
            Agent,
            agent_type=self.AGENT_TYPE,
            config={"agent_args": "not_a_dict", "prompt_input": {}, "prompt_extension": {}, "tool_config": {}},
        )
        mock_registry_instance = Mock()
        mock_registry_instance.get_agent_class_by_type.return_value = self.MOCK_AGENT_CLASS
        mock_agent_registry.return_value = mock_registry_instance

        call_command("verifyagents")

        corrupted_agent.refresh_from_db()
        assert corrupted_agent.corrupted is True

    def test_verifyagents_command_empty_database(self):
        Agent.objects.all().delete()

        with patch("agent.management.commands.verifyagents.AgentRegistry") as mock_agent_registry:
            mock_registry_instance = Mock()
            mock_agent_registry.return_value = mock_registry_instance

            call_command("verifyagents")
