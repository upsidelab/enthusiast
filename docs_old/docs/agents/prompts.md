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

## ReAct Agent Prompts
There is one specific prompt template type, designed to be used with `BaseReActAgent` class, it could be found in `@enthusiast-agent-re-act` package:

```python
from enthusiast_agent_re_act import TEMPLATE_RE_ACT_PROMPT
```

### ReAct Prompt Structure

ReAct agents use structured prompts that guide the reasoning process:

#### Template Structure

The ReAct prompt template is divided into several key sections, each serving a specific purpose:
**1. Agent Instructions & Role**
Defines the agent's purpose and approach. Sets the overall context for the ReAct methodology. 
````python
TEMPLATE_RE_ACT_PROMPT = """
# 1. AGENT INSTRUCTIONS & ROLE
I want you to help full fill a request using (Reasoning and Acting) approach.
"""
````
**2. Tool Specification Format**
Shows the exact JSON structure for tool actions. Defines the required format for tool calls.
````python
"""Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
"""
````
**3. Reasoning Process Framework**
Establishes the step-by-step thinking pattern. Defines the core ReAct loop structure.
````python
"""For each step, follow the format:
User query: the user's question or request
Thought: what you should do next
Action: 
{{
  "action": "<tool>",
  "action_input": {{"<tool_argument_name>": "<tool_argument_value>", ...}}
}}
Observation: the result returned by the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have the necessary information
Final Answer: the response to the user"""
````
**4. Available Resources**
Lists tools and their capabilities. Provides context for tool selection.

````python
"""Here are the tools you can use:
{tools}"""
````
**5. First Example**
Shows a complete product search workflow. Demonstrates tool chaining and verification.
````python
"""Example 1:
User query: I want to buy a blue van.
Thought: I need to find products which meets user criteria.
Action: {{
 "action": the tool to use, one of [{tool_names}],
 "action_input": {{"<tool_argument_name>": "<tool_argument_value>", ...}}
 }}
Observation: I got one car.
Thought: I need to verify if this product meets user's criteria.
Action:
 {{
 "action": the verification tool to use, one of [{tool_names}],
 "action_input": {{"<tool_argument_name>": "<tool_argument_value>", ...}}
 }}
Observation: I got a car that meets users criteria.
Final Answer: This car may suits your needs - Blue Mercedes Sprinter 2025"""
````
**6. Second Example**
Shows iterative refinement. Demonstrates asking for more information.
````python
"""Example 2:
User query: I'm looking for a pc
Thought: I need to find products which meets user criteria.
Action: 
{{
"action": the tool to use, one of [{tool_names}],
"action_input": {{"<tool_argument_name>": "<tool_argument_value>", ...}}
}}
Observation: There a lot of pc
Thought: Now I need to limit this number by providing more criteria
Final Answer: What operating system you prefer Windows or MacOS?"""
````
**7. Output Constraints**
Defines response format requirements. Sets strict boundaries for agent output.
````python
"""Do not came up with any other types of JSON than specified above.
Your output to user should always begin with '''Final Answer: <output>'''"""
````
**8. Execution Trigger**
Signals the agent to start processing. Provides runtime context variables.

````python
"""
Begin!
Chat history: {chat_history}
User query: {input}
{agent_scratchpad}"""
````

**Section Breakdown:**

1. **Agent Instructions & Role**: Defines the agent's purpose and approach
2. **Tool Specification Format**: Shows the exact JSON structure for tool actions
3. **Reasoning Process Framework**: Establishes the step-by-step thinking pattern
4. **Available Resources**: Lists tools and their capabilities
5. **Concrete Examples**: Provides real-world usage examples
6. **Output Constraints**: Defines response format requirements
7. **Execution Trigger**: Signals the agent to start processing


## Summary

Prompts in Enthusiast provide a powerful and flexible foundation for agent behavior:

- **Multiple Types**: Support for both text-based and chat-based prompts
- **ReAct Integration**: Specialized prompts for reasoning and acting agents
- **Context Management**: Rich context and conversation history support
- **Configuration-Driven**: Flexible configuration through the agent config system
- **Best Practices**: Established patterns for effective prompt design

By understanding and effectively using the prompt system, developers can create agents that exhibit sophisticated reasoning, clear communication, and effective tool usage while maintaining flexibility and extensibility.
