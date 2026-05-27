from unittest.mock import MagicMock

from enthusiast_common.agents.base import BaseAgent
from pydantic import BaseModel


class _StubToolConfig:
    """Minimal tool config entry for testing."""

    def __init__(self, tool_class, tool_configuration_args=None):
        self.tool_class = tool_class
        self.tool_configuration_args = tool_configuration_args


class _BaseStubAgent:
    """Minimal agent-like object for testing set_runtime_arguments without metaclass validation."""

    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None
    TOOLS = []

    def __init__(self, tools):
        self._tools = tools


def test_set_runtime_arguments_injects_config_by_tool_name():
    tool = MagicMock()
    tool.NAME = "my_tool"

    class StubSchema(BaseModel):
        proxy: str

    class StubAgent(_BaseStubAgent):
        TOOLS = [_StubToolConfig(tool_class=tool, tool_configuration_args=StubSchema)]

    agent = StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"my_tool": {"proxy": "http://example.com"}},
    })

    tool.set_runtime_arguments.assert_called_once_with(
        {"proxy": "http://example.com"}, schema=StubSchema
    )


def test_set_runtime_arguments_passes_none_schema_for_tools_without_config():
    """Tools with no tool_configuration_args on their TOOLS entry get schema=None."""
    tool = MagicMock()
    tool.NAME = "my_tool"

    class StubAgent(_BaseStubAgent):
        TOOLS = [_StubToolConfig(tool_class=tool, tool_configuration_args=None)]

    agent = StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"my_tool": {}},
    })

    tool.set_runtime_arguments.assert_called_once_with({}, schema=None)


def test_set_runtime_arguments_skips_tool_absent_from_tool_config():
    """Tools not in tool_config are not called — e.g. StopExecutionTool."""
    tool = MagicMock()
    tool.NAME = "stop_execution"

    class StubAgent(_BaseStubAgent):
        TOOLS = [_StubToolConfig(tool_class=tool)]

    agent = StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {},
    })

    tool.set_runtime_arguments.assert_not_called()


def test_set_runtime_arguments_tolerates_missing_tool_config_key():
    """Old-format configs without a tool_config key must not crash."""
    tool = MagicMock()
    tool.NAME = "my_tool"

    class StubAgent(_BaseStubAgent):
        TOOLS = [_StubToolConfig(tool_class=tool)]

    agent = StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
    })

    tool.set_runtime_arguments.assert_not_called()


def test_set_runtime_arguments_only_injects_matching_tool():
    """When multiple tools are present, only the matching one receives its config."""
    tool_a = MagicMock()
    tool_a.NAME = "tool_a"
    tool_b = MagicMock()
    tool_b.NAME = "tool_b"

    class SchemaA(BaseModel):
        key: str

    class StubAgent(_BaseStubAgent):
        TOOLS = [
            _StubToolConfig(tool_class=tool_a, tool_configuration_args=SchemaA),
            _StubToolConfig(tool_class=tool_b),
        ]

    agent = StubAgent(tools=[tool_a, tool_b])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"tool_a": {"key": "value"}},
    })

    tool_a.set_runtime_arguments.assert_called_once_with({"key": "value"}, schema=SchemaA)
    tool_b.set_runtime_arguments.assert_not_called()
