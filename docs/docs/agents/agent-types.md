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

Those arguments can be accessed by agent like this:

```python

    def get_answer(self, input_text: str) -> str:
        agent_output = self._agent_executor.invoke(
            {"input": input_text, "product_type": self.PROMPT_INPUT.product_type}
        )
        return agent_output["output"]

```

## ReAct Agent

### Overview

The `BaseReActAgent` implements the ReAct (Reasoning + Acting) pattern, which enables agents to:

- **Reason**: Think through problems step by step
- **Act**: Use tools to gather information or perform actions
- **Observe**: Process tool results and continue reasoning
- **Iterate**: Repeat the process until a solution is reached

It also comes with attached ReAct-style output parser and structured tools description, which allows to use it with multiple input arguments tools with ease.

### Implementation

```python
class BaseReActAgent(BaseAgent):
    def get_answer(self, input_text: str) -> str:
        # Build and execute the agent
        agent_executor = self._build_agent_executor()
        response = agent_executor.invoke(
            {"input": input_text}, 
            config=self._build_invoke_config()
        )
        return response["output"]

    def _build_tools(self) -> list[BaseTool]:
        """Convert internal tools to LangChain tools"""
        return [tool.as_tool() for tool in self._tools]

    def _build_memory(self) -> BaseMemory:
        """Use limited memory for ReAct reasoning"""
        return self._injector.chat_limited_memory

    def _build_invoke_config(self) -> dict[str, Any]:
        """Configure callback handlers"""
        if self._callback_handler:
            return {"callbacks": [self._callback_handler]}
        return {}

    def _build_agent_executor(self) -> AgentExecutor:
        """Create the LangChain agent executor"""
        tools = self._build_tools()
        agent = create_react_agent(
            tools=tools,
            llm=self._llm,
            prompt=self._prompt,
            tools_renderer=render_text_description_and_args,
            output_parser=StructuredReActOutputParser(),
        )
        return AgentExecutor(agent=agent, tools=tools, memory=self._build_memory())
```

### ReAct Reasoning Process

The ReAct agent follows a structured reasoning process:

1. **Input Analysis**: Parse and understand the user's request
2. **Reasoning**: Think through the problem step by step
3. **Action Selection**: Choose appropriate tools to use
4. **Tool Execution**: Execute selected tools with parameters
5. **Observation**: Process tool results and observations
6. **Iteration**: Continue reasoning based on new information
7. **Final Answer**: Provide a comprehensive response

### Structured Output Parsing

The ReAct agent uses a structured output parser that expects:

```json
{
  "action": "tool_name",
  "action_input": {
    "parameter1": "value1",
    "parameter2": "value2"
  }
}
```

Or for final answers:

```
Final Answer: The comprehensive response to the user's question
```

## Summary

The Enthusiast agent system provides a robust foundation for building intelligent, tool-using agents:

- **BaseAgent**: Abstract base class with required interface and validation
- **BaseReActAgent**: Concrete implementation of the ReAct reasoning pattern

By following the established patterns and implementing the required interfaces, developers can create powerful, specialized agents that leverage the full capabilities of the Enthusiast framework.
