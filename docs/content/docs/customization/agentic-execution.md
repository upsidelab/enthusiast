---
sidebar_position: 5
---

# Creating an Agentic Execution

Agentic executions allow you to run an agent autonomously as a programmatic batch job — no user interaction required. This guide walks through adding an agentic execution definition to an agent plugin.

## When to use

Use agentic executions when you want to:
- Trigger an agent job programmatically or on a schedule
- Process a batch of items without user interaction
- Return structured output from an agent as an API response

## Implementation

### 1. Define the input schema

Create a Pydantic model describing what callers must supply. The server derives the JSON schema from this class and validates incoming requests against it.

```python
from enthusiast_common.agentic_execution import ExecutionInputType

class MyExecutionInput(ExecutionInputType):
    additional_instructions: str | None = None
    item_ids: list[str] | None = None
```

### 2. Define failure codes (optional)

If your execution has domain-specific failure modes, extend `ExecutionFailureCode`:

```python
from enthusiast_common.agentic_execution import ExecutionFailureCode

class MyFailureCode(ExecutionFailureCode):
    EXTERNAL_SERVICE_UNAVAILABLE = "external_service_unavailable"
    INSUFFICIENT_DATA = "insufficient_data"
```

### 3. Write validators

Validators inspect the agent's response after each `execute()` call. They return a `ValidatorResponse` that tells the run loop whether to succeed, retry, or stop.

```python
from enthusiast_common.agentic_execution import (
    BaseExecutionValidator,
    ExecutionInputType,
    ToolScratchpad,
    ValidatorResponse,
)

class MyOutputValidator(BaseExecutionValidator):
    def validate(
        self,
        response: str,
        execution_input: ExecutionInputType,
        tool_scratchpad: ToolScratchpad | None = None,
    ) -> ValidatorResponse:
        if "expected_field" not in response:
            return ValidatorResponse(
                validation_successful=False,
                retry_needed=True,
                feedback="Response must include 'expected_field'. Please try again.",
            )
        return ValidatorResponse(validation_successful=True)
```

Set `retry_needed=False` when retrying is pointless — for example, when an external system is unreachable. The run loop stops immediately and uses `feedback` as the failure summary shown to users.

### 4. Create the execution definition

Subclass `BaseAgenticExecutionDefinition` and implement `execute()`. This is the single-attempt logic the run loop calls repeatedly until validators pass or retries are exhausted.

```python
from enthusiast_common.agentic_execution import (
    BaseAgenticExecutionDefinition,
    IsValidJsonValidator,
    StopExecutionValidator,
)
from enthusiast_common.agentic_execution.protocol import ExecutionConversationInterface

from .inputs import MyExecutionInput
from .validators import MyOutputValidator
from .errors import MyFailureCode


class MyAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    EXECUTION_KEY = "my-agent-execution"
    AGENT_KEY = "enthusiast-agent-my-agent"
    NAME = "My Execution"
    DESCRIPTION = "Runs the my-agent batch job."

    INPUT_TYPE = MyExecutionInput
    VALIDATORS = [StopExecutionValidator, IsValidJsonValidator, MyOutputValidator]
    FAILURE_CODES = MyFailureCode

    def execute(
        self,
        input_data: MyExecutionInput,
        conversation: ExecutionConversationInterface,
    ) -> str:
        prompt = input_data.additional_instructions or "Process all items and return results as JSON."
        return conversation.ask(prompt)
```

`execute()` sends a message to the agent and returns its raw response string. The base `run()` method handles passing that response through `VALIDATORS`, sending feedback on failure, and retrying.

### 5. Update the agent config provider

Execution runs benefit from a stripped-down system prompt that removes conversational scaffolding and mandates structured output. Implement this in your `BaseAgentConfigProvider`:

```python
from enthusiast_common.agents.config import BaseAgentConfigProvider, ConfigType
from enthusiast_common.config import AgentConfigWithDefaults

from .prompts import CONVERSATION_PROMPT, EXECUTION_PROMPT


class MyAgentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        system_prompt = (
            EXECUTION_PROMPT
            if config_type == ConfigType.AGENTIC_EXECUTION_DEFINITION
            else CONVERSATION_PROMPT
        )
        return AgentConfigWithDefaults(prompt_template=..., system_prompt=system_prompt)
```

Agents that don't need context-specific behaviour can ignore `config_type` and always return the same configuration.

### 6. Register the definition

Add the dotted import path to `settings_override.py`:

```python
AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [
    "my_agent.MyAgenticExecutionDefinition",
]
```

The server discovers registered classes at startup via `AgenticExecutionDefinitionRegistry`, which follows the same pattern as `AVAILABLE_AGENTS`.

## Using `ToolScratchpad`

Tools and validators can share data within a single execution attempt via `ToolScratchpad`. The scratchpad is cleared before each retry so validators always see only results from the current attempt.

**In your tool:**
```python
def run(self, ...):
    result = {"item_a": True, "item_b": False}
    self.tool_scratchpad.record("my_tool", result)
    return result
```

**In your validator:**
```python
def validate(self, response, execution_input, tool_scratchpad=None):
    if tool_scratchpad:
        results = tool_scratchpad.read("my_tool")
        if results and any(not v for v in results.values()):
            failed = [k for k, v in results.items() if not v]
            return ValidatorResponse(
                validation_successful=False,
                retry_needed=True,
                feedback=f"The following items failed: {failed}. Please retry.",
            )
    return ValidatorResponse(validation_successful=True)
```
