---
sidebar_position: 2
---

# Agent Types

Enthusiast provides a flexible and extensible agent system built on abstract base classes that define the core architecture and capabilities. The system supports multiple agent types, each designed for different use cases and reasoning strategies.

## Overview

The agent system in Enthusiast is built on a foundation of abstract base classes that provide:

- **Standardized Interface**: Common methods and properties all agents must implement
- **Configuration Management**: Runtime configuration through structured schemas
- **Tool Integration**: Seamless integration with the tool system
- **Memory Management**: Built-in conversation memory and context management
- **Extensibility**: Easy creation of custom agent types

## Base Agent

### Core Components

Every agent in Enthusiast consists of:

- **Language Model**: The underlying LLM for reasoning and text generation
- **Tools**: Collection of tools the agent can use
- **Prompt Template**: Instructions and context for the agent
- **Injector**: Access to external resources and services
- **Callback Handlers(Optional)**: Handling LLM and agent events

### Core Interface

The `BaseAgent` class defines the fundamental interface all agents must implement:

### Required Class Variables

The `ExtraArgsClassBaseMeta` metaclass enforces that all agent implementations define:

#### `AGENT_ARGS` (RequiredFieldsModel)
Configuration schema for agent-specific parameters:

```python
class AgentConfiguration(RequiredFieldsModel):
    max_iterations: int = Field(title="Max Iterations", description="Maximum reasoning steps", default=10)
    enable_debugging: bool = Field(title="Enable Debugging", description="Enable detailed logging", default=False)

class ExampleAgent(BaseAgent):
    AGENT_ARGS = AgentConfiguration
```

#### `PROMPT_INPUT` (RequiredFieldsModel)
Schema for prompt input variables:

```python
class PromptInputSchema(RequiredFieldsModel):
    product_type: str = Field(title="Product type", description="Product type agent with work with")
    context: str = Field(title="Context", description="Additional context information")
    output_format: str = Field(title="Output Format", description="Expected response format")

class ExampleAgent(BaseAgent):
    PROMPT_INPUT = PromptInputSchema
```

#### `PROMPT_EXTENSION` (RequiredFieldsModel)
Schema for prompt extension variables:

```python
class PromptExtensionSchema(RequiredFieldsModel):
    system_instructions: str = Field(title="System Instructions", description="Agent behavior instructions")
    restrictions: str = Field(title="Restriction instructions", description="Restricted agent behaviours")

class ExampleAgent(BaseAgent):
    PROMPT_EXTENSION = PromptExtensionSchema
```

#### `TOOLS` (list[BaseTool])
List of tools configurations:

```python
class ExampleAgent(BaseAgent):
    TOOLS = [
        LLMToolConfig(tools_class=ExampleTool),
        LLMToolConfig(tools_class=ExampleTool),
    ]
```

Those arguments can be accessed inside the agent. For example, `_get_system_prompt_variables()` is called before each invocation to resolve `{variable}` placeholders in the system prompt:

```python

    def _get_system_prompt_variables(self) -> dict:
        return {"output_format": self.PROMPT_INPUT.output_format}

```

## Tool Calling Agent

### Overview

The `BaseToolCallingAgent` implements the standard tool calling pattern, leveraging native function calling support built into all modern LLMs. It is the recommended base class for all custom agents.

### Implementation

```python
class BaseToolCallingAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        history = self._injector.chat_history
        compactor = self._injector.memory_compactor

        agent = self._build_agent()
        
        # Build conversation context with last users message appended
        context_messages = self._build_context_messages()
        input_messages = context_messages + [HumanMessage(content=input_text)]
        
        # Execute the agent
        result = agent.invoke({"messages": input_messages}, config=self._build_invoke_config())

        # Slice off only the new messages produced this turn, then persist them to the history
        new_messages = result["messages"][len(context_messages):]
        final_message = next(
            m for m in reversed(new_messages)
            if isinstance(m, AIMessage) and not m.tool_calls
        )
        history.add_messages(new_messages)

        # If the memory compactor is present, execute it
        if compactor:
            compactor.compact_if_needed()

        return final_message.text

    def _build_context_messages(self) -> list[BaseMessage]:
        """Build conversation history trimmed to 'MAX_HISTORY_TOKENS' number of tokens. 
        With memory compactor present, the conversation summary will also be included for longer conversations."""
        return ContextWindowBuilder(
            chat_history=self._injector.chat_history,
            memory_compactor=self._injector.memory_compactor,
        ).build(max_tokens=MAX_HISTORY_TOKENS)

    def _build_tools(self) -> list[BaseTool]:
        """Convert internal tools to LangChain BaseTool instances."""
        return [tool.as_tool() for tool in self._tools]

    def _get_system_prompt(self) -> str:
        """Resolve template variables in the system prompt string via _get_system_prompt_variables()."""
        return self._system_prompt.format(**self._get_system_prompt_variables())

    def _build_invoke_config(self) -> dict[str, Any]:
        """Pass callback handler to the agent invocation if one is configured."""
        if self._callback_handler:
            return {"callbacks": [self._callback_handler]}
        return {}

    def _build_agent(self):
        """Build a LangGraph agent with the configured LLM, tools, and system prompt."""
        return create_agent(
            model=self._llm,
            tools=self._build_tools(),
            system_prompt=self._get_system_prompt(),
        )
```

## Summary

The Enthusiast agent system provides a robust foundation for building intelligent, tool-using agents:

- **BaseAgent**: Abstract base class with required interface and validation
- **BaseToolCallingAgent**: Standard implementation using native LLM tool calling

By following the established patterns and implementing the required interfaces, developers can create powerful, specialized agents that leverage the full capabilities of the Enthusiast framework.
