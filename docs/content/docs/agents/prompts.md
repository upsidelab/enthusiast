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

## Supported Prompt Types

Enthusiast supports two main prompt types, each designed for different use cases:

### 1. PromptTemplate

Single text template with variable placeholders

### 2. ChatPromptTemplate

Multi-message template with conversational interactions

## Configuration

### Prompt Configuration Structure

Prompts are configured through the `AgentConfig`:

```python
class AgentConfig(ArbitraryTypeBaseModel, Generic[InjectorT]):
    # ... other configuration fields ...
    
    prompt_template: Optional[PromptTemplateConfig] = None
    chat_prompt_template: Optional[ChatPromptTemplateConfig] = None

```

### PromptTemplate Configuration

```python
class PromptTemplateConfig(ArbitraryTypeBaseModel):
    input_variables: list[str]    # List of variable names used in the template
    template: str                 # The prompt template string
```

**Example Configuration**:
```python
prompt_template=PromptTemplateConfig(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template=EXAMPLE_AGENT_PROMPT_TEMPLATE
)
```

### ChatPromptTemplate Configuration

```python
class ChatPromptTemplateConfig(ArbitraryTypeBaseModel):
    messages: Sequence[MessageLikeRepresentation]  # List of message components
```

**Example Configuration**:
```python
chat_prompt_template=ChatPromptTemplateConfig(
    messages=[
        ("system", "You are a sales support agent, and you know everything about a company and their products."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
```

## Prompt Construction

### Builder Integration

The `AgentBuilder` automatically constructs the appropriate prompt type based on configuration:

```python
def _build_prompt_template(self) -> BasePromptTemplate:
    """Build the prompt template for the agent"""
    if self._config.prompt_template:
        # Use text-based prompt template
        return PromptTemplate(
            input_variables=self._config.prompt_template.input_variables,
            template=self._config.prompt_template.template,
        )
    else:
        # Use chat-based prompt template
        return ChatPromptTemplate.from_messages(
            messages=self._config.chat_prompt_template.messages
        )
```

## Summary

Prompts in Enthusiast provide a powerful and flexible foundation for agent behavior:

- **Multiple Types**: Support for both text-based and chat-based prompts
- **Context Management**: Rich context and conversation history support
- **Configuration-Driven**: Flexible configuration through the agent config system
- **Best Practices**: Established patterns for effective prompt design

By understanding and effectively using the prompt system, developers can create agents that exhibit sophisticated reasoning, clear communication, and effective tool usage while maintaining flexibility and extensibility.
