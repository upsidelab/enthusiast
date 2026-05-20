---
sidebar_position: 6
---

# Prompts

Prompts are the foundation of agent behavior and communication in the Enthusiast framework. They define how agents understand user input, process context, and generate responses. Enthusiast supports multiple prompt types and provides flexible configuration options for different use cases.

## Overview

Prompts in Enthusiast serve several key purposes:

- **Agent Instructions**: Define the agent's role, capabilities, and behavior
- **Tool Integration**: Provide context about available tools and their usage
- **Reasoning Framework**: Establish the thinking and reasoning patterns for agents
- **Output Formatting**: Define the expected structure and format of responses
- **Context Management**: Handle conversation history and current context

## Configuration

The agent system prompt is a plain string passed via `AgentConfig.system_prompt`:

```python
# prompt.py (conventional location)
MY_AGENT_SYSTEM_PROMPT = """
You are a helpful assistant...
"""
```

```python
# config.py

class ExampleConfig(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        return AgentConfigWithDefaults(
            system_prompt=MY_AGENT_SYSTEM_PROMPT,
            agent_class=MyAgent,
            tools=MyAgent.TOOLS,
        )
```

## Template Variables

If the system prompt contains `{variable}` placeholders, override `_get_system_prompt_variables()` in the agent class:

```python
class MyAgent(BaseToolCallingAgent):
    def _get_system_prompt_variables(self) -> dict:
        return {"output_format": self.PROMPT_INPUT.output_format}
```

The base implementation returns `{}`, so agents with static prompts require no override.

## Summary

Prompts in Enthusiast provide a powerful and flexible foundation for agent behavior:

- **Plain string**: System prompt is a `str` passed directly to the LLM via LangGraph
- **Context Management**: Conversation history and token limiting handled automatically by `BaseToolCallingAgent`
- **Configuration-Driven**: Prompt passed through the agent config system

By understanding and effectively using the prompt system, developers can create agents that exhibit sophisticated reasoning, clear communication, and effective tool usage while maintaining flexibility and extensibility.
