from typing import Any
from unittest.mock import patch

import pytest
from enthusiast_common.config import FunctionToolConfig
from enthusiast_common.tools import BaseFunctionTool
from pydantic import BaseModel
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolConfigField


class DummySchema(BaseModel):
    value_1: str
    value_2: int


class BadSchema(BaseModel):
    value: int


class DummyTool(BaseFunctionTool):
    NAME = "dummy_tool"
    CONFIGURATION_ARGS = DummySchema


class DummyTool2(BaseFunctionTool):
    NAME = "dummy_tool_2"
    CONFIGURATION_ARGS = DummySchema


def get_model_serializer(
    agent_field_name: str,
    data,
):
    class FieldTestSerializer(serializers.Serializer):
        config = PydanticModelField(agent_field_name=agent_field_name)

    return FieldTestSerializer(data=data, context={"agent_type": "dummy_agent"})


def get_tool_config_serializer(agent_field_name: str, tool_field_name: str, data: Any):
    class FieldTestSerializer(serializers.Serializer):
        config = PydanticModelToolConfigField(agent_field_name=agent_field_name, tool_field_name=tool_field_name)

    return FieldTestSerializer(data=data, context={"agent_type": "dummy_agent"})



@pytest.fixture
def agent_context():
    return {"agent_type": "dummy_agent"}


@pytest.fixture
def available_agents():
    return [ "dummy_path.AgentClass" ]


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_field_valid(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"AGENT_ARGS": DummySchema})
    input_data = {"config": {"value_1": "John", "value_2": 30}}

    serializer = get_model_serializer(agent_field_name="AGENT_ARGS", data=input_data)

    assert serializer.is_valid(raise_exception=True)


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_field_invalid_data(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"AGENT_ARGS": DummySchema})
    input_data = {"config": {"value_1": "John"}}
    serializer = get_model_serializer(agent_field_name="AGENT_ARGS", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "value_2" in str(e.value)


def test_pydantic_model_field_missing_context():
    field = PydanticModelField(agent_field_name="AGENT_ARGS")
    with pytest.raises(AssertionError) as e:
        field.to_internal_value({})
    assert "agent_type" in str(e.value)


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type", side_effect=ImportError("failed"))
def test_pydantic_model_field_import_error(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    input_data = {"config": {}}
    serializer = get_model_serializer(agent_field_name="AGENT_ARGS", data=input_data)

    with pytest.raises(APIException) as e:
        serializer.is_valid(raise_exception=True)
    assert "Error loading agent" in str(e.value)



@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_valid(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool2)]}
    )
    input_data = {"config": {"dummy_tool": {"value_1": "Alice", "value_2": 25}}}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS", data=input_data)

    serializer.is_valid(raise_exception=True)

    assert serializer.data == input_data


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_invalid_type(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool)]}
    )
    input_data = {"config": [{"value_1": "Alice", "value_2": 25}]}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Expected a dict" in str(e.value)


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_unknown_tool_name(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool)]}
    )
    input_data = {"config": {"nonexistent_tool": {"value_1": "Alice", "value_2": 25}}}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    error_detail = e.value.detail["config"]["nonexistent_tool"]
    assert isinstance(error_detail, list)
    assert "Unknown tool" in str(error_detail[0])


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_invalid_field_values(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent", (), {"TOOLS": [FunctionToolConfig(tool_class=DummyTool), FunctionToolConfig(tool_class=DummyTool2)]}
    )
    input_data = {"config": {
        "dummy_tool": {"value_1": "Missing value_2"},
        "dummy_tool_2": {"value_2": 99},
    }}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS", data=input_data)

    serializer.is_valid()

    assert "dummy_tool" in serializer.errors["config"]
    assert "dummy_tool_2" in serializer.errors["config"]


@patch("agent.core.registries.agents.agent_registry.settings")
@patch("agent.serializers.customs.fields.AgentRegistry.get_agent_class_by_type")
def test_pydantic_model_tool_config_field_tool_without_config_args_is_invalid_key(
    mock_import, mock_settings, available_agents
):
    """A tool with CONFIGURATION_ARGS=None must not be a valid key."""

    class NoConfigTool:
        NAME = "no_config_tool"
        CONFIGURATION_ARGS = None

    class MockToolConfigEntry:
        def __init__(self, tool_class):
            self.tool_class = tool_class

    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type(
        "Agent",
        (),
        {
            "TOOLS": [
                MockToolConfigEntry(DummyTool),
                MockToolConfigEntry(NoConfigTool),
            ]
        },
    )
    input_data = {"config": {"no_config_tool": {}}}
    serializer = get_tool_config_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION_ARGS", data=input_data)

    with pytest.raises(serializers.ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Unknown tool" in str(e.value)
