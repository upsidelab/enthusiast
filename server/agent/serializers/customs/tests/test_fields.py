from typing import Any
from unittest.mock import patch

import pytest
from pydantic import BaseModel
from rest_framework import serializers
from rest_framework.exceptions import APIException, ValidationError

from agent.serializers.customs.fields import PydanticModelField, PydanticModelToolListField


class DummySchema(BaseModel):
    value_1: str
    value_2: int


class BadSchema(BaseModel):
    value: int


class DummyTool:
    CONFIGURATION = DummySchema


def get_model_serializer(
    agent_field_name: str,
    data,
):
    class FieldTestSerializer(serializers.Serializer):
        config = PydanticModelField(agent_field_name=agent_field_name)

    return FieldTestSerializer(data=data, context={"agent_key": "dummy_agent"})


def get_list_model_serializer(agent_field_name: str, tool_field_name: str, data: Any):
    class FieldTestSerializer(serializers.Serializer):
        config = PydanticModelToolListField(agent_field_name=agent_field_name, tool_field_name=tool_field_name)

    return FieldTestSerializer(data=data, context={"agent_key": "dummy_agent"})


@pytest.fixture
def agent_context():
    return {"agent_key": "dummy_agent"}


@pytest.fixture
def available_agents():
    return {
        "dummy_agent": {"agent": "dummy.path.AgentClass"},
    }


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
def test_pydantic_model_field_valid(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"AGENT_ARGS": DummySchema})
    input_data = {"config": {"value_1": "John", "value_2": 30}}

    serializer = get_model_serializer(agent_field_name="AGENT_ARGS", data=input_data)

    assert serializer.is_valid(raise_exception=True)


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
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
    assert "agent_key" in str(e.value)


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string", side_effect=ImportError("failed"))
def test_pydantic_model_field_import_error(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    input_data = {"config": {}}
    serializer = get_model_serializer(agent_field_name="AGENT_ARGS", data=input_data)

    with pytest.raises(APIException) as e:
        serializer.is_valid(raise_exception=True)
    assert "Error loading agent" in str(e.value)


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
def test_pydantic_model_tool_list_field_valid(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"TOOLS": [DummyTool, DummyTool]})
    input_data = {"config": [{"value_1": "Alice", "value_2": 25}, {"value_1": "Bob", "value_2": 30}]}
    serializer = get_list_model_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    serializer.is_valid(raise_exception=True)

    assert serializer.data == input_data


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
def test_pydantic_model_tool_list_field_invalid_configs_number(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"TOOLS": [DummyTool]})
    input_data = {"config": []}
    serializer = get_list_model_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Mismatch between number of tools and provided configs." in str(e.value)


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
def test_pydantic_model_tool_list_field_invalid_config_type(mock_import, mock_settings, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"TOOLS": [DummyTool]})
    input_data = {"config": {}}
    serializer = get_list_model_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
    assert "Expected a list of tool configurations." in str(e.value)


@patch("agent.serializers.customs.fields.settings")
@patch("agent.serializers.customs.fields.import_from_string")
def test_pydantic_model_tool_list_field_invalid_data(mock_import, mock_settings, agent_context, available_agents):
    mock_settings.AVAILABLE_AGENTS = available_agents
    mock_import.return_value = type("Agent", (), {"TOOLS": [DummyTool, DummyTool]})
    input_data = {"config": [{"value_1": "Missing age"}, {"value_2": 28}]}
    serializer = get_list_model_serializer(agent_field_name="TOOLS", tool_field_name="CONFIGURATION", data=input_data)

    serializer.is_valid()

    assert len(serializer.errors["config"]) == 2
    assert "value_2" in serializer.errors["config"][0].keys()
    assert "value_1" in serializer.errors["config"][1].keys()
