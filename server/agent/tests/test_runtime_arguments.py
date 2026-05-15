from unittest.mock import MagicMock
from enthusiast_common.agents.base import BaseAgent


class _StubAgent:
    """Minimal agent-like object for testing set_runtime_arguments without metaclass validation."""
    AGENT_ARGS = None
    PROMPT_INPUT = None
    PROMPT_EXTENSION = None

    def __init__(self, tools):
        self._tools = tools


def test_set_runtime_arguments_injects_config_by_tool_name():
    tool = MagicMock()
    tool.NAME = "my_tool"
    agent = _StubAgent(tools=[tool])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"my_tool": {"proxy": "http://example.com"}},
    })

    tool.set_runtime_arguments.assert_called_once_with({"proxy": "http://example.com"})


def test_set_runtime_arguments_skips_tool_absent_from_tool_config():
    """Tools with no CONFIGURATION_ARGS (e.g. StopExecutionTool) won't have a tool_config entry — must not crash."""
    tool = MagicMock()
    tool.NAME = "stop_execution"
    agent = _StubAgent(tools=[tool])

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
    agent = _StubAgent(tools=[tool])

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
    agent = _StubAgent(tools=[tool_a, tool_b])

    BaseAgent.set_runtime_arguments(agent, {
        "agent_args": {},
        "prompt_input": {},
        "prompt_extension": {},
        "tool_config": {"tool_a": {"key": "value"}},
    })

    tool_a.set_runtime_arguments.assert_called_once_with({"key": "value"})
    tool_b.set_runtime_arguments.assert_not_called()
