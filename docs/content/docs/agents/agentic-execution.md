---
sidebar_position: 9
---

# Agentic Execution

Agentic execution is a first-class concept distinct from the conversation-based agent flow. Where conversations are interactive (between the user and the agent), executions are **autonomous, programmatic batch jobs**: submitted via API, the LLM agent runs to completion without user interaction, and the caller inspects the result afterward.

Each execution is tightly coupled to a configured `Agent` instance, which already carries the dataset association, system prompt, and tool configuration needed to run.

## Core Abstractions

### `ExecutionStatus`

Enum tracking the lifecycle of an execution:

- **`PENDING`**: Execution has been created; the Celery task has not started yet
- **`IN_PROGRESS`**: The Celery task is actively running the agent
- **`FINISHED`**: The execution completed successfully
- **`FAILED`**: The execution ended with an error or validation failure

### `ExecutionResult`

Dataclass returned by `BaseAgenticExecutionDefinition.run()`. Communicates the full outcome without raising exceptions.

- **`success`** (`bool`): Whether the execution completed successfully
- **`output`** (`dict`): Structured output payload — meaningful only when `success=True`
- **`failure_code`** (`ExecutionFailureCode | None`): Standardised failure code, set when `success=False`
- **`failure_summary`** (`str | None`): LLM-generated plain-language explanation of what went wrong

### `ExecutionFailureCode`

`StrEnum` defining standardised failure codes. Plugins can extend this enum to add execution-specific codes and point `FAILURE_CODES` at the subclass.

### `ExecutionInputType`

Pydantic `BaseModel` subclassed per plugin to declare and validate structured execution input. The server derives the JSON Schema from it for API responses and request validation.

### `ToolScratchpad`

A dict-based store that tools write to and validators read from during a single execution attempt. One instance is created per execution conversation. It is cleared before each retry so validators always see only results from the current attempt.

## Validators

### `ValidatorResponse`

Structured return value from `BaseExecutionValidator.validate()`:

- **`validation_successful`** (`bool`): Whether the response passed this validator
- **`retry_needed`** (`bool`): Whether the run loop should retry after failure — default `True`
- **`feedback`** (`str | None`): Message sent back to the LLM when `retry_needed=True`; used as `failure_summary` when `retry_needed=False`

### `BaseExecutionValidator`

Abstract base class for response validators. Receives the raw response string, the execution input, and the `ToolScratchpad`, and returns a `ValidatorResponse`.

```python
class BaseExecutionValidator(ABC):
    def validate(
        self,
        response: str,
        execution_input: ExecutionInputType,
        tool_scratchpad: Optional[ToolScratchpad] = None,
    ) -> ValidatorResponse:
        ...
```

The run loop processes the first failing `ValidatorResponse` it encounters:

- All validators return `validation_successful=True` → execution succeeds
- `validation_successful=False, retry_needed=True` → `feedback` is sent back to the LLM and the attempt retries (up to `MAX_RETRIES` times)
- `validation_successful=False, retry_needed=False` → the loop stops immediately; `failure_code` is set to `validation_failed` and `feedback` becomes the `failure_summary`

### Built-in Validators

**`IsValidJsonValidator`** — validates that the agent's response is a valid JSON string. On failure, retries with corrective feedback.

**`StopExecutionValidator`** — checks whether the agent called the stop execution tool during the attempt. If it did, halts the run without retrying using the recorded stop reason as the failure summary. Place this first in `VALIDATORS` so it short-circuits before any other checks.

## Execution Definition

### `BaseAgenticExecutionDefinition`

The base class provides a concrete `run()` that implements the validator retry loop, and an abstract `execute()` that subclasses fill in with the actual per-attempt logic.

**Class-level declarations:**

#### `EXECUTION_KEY`
- **Type**: `ClassVar[str]`
- **Description**: Unique slug identifying and persisting this execution type

#### `AGENT_KEY`
- **Type**: `ClassVar[str]`
- **Description**: Must match the `AGENT_KEY` of the target agent plugin. Multiple execution definition classes may share the same `AGENT_KEY`.

#### `NAME` / `DESCRIPTION`
- **Type**: `ClassVar[str]` / `ClassVar[Optional[str]]`
- **Description**: Human-readable label and optional longer description shown in the execution type selector

#### `INPUT_TYPE`
- **Type**: `ClassVar[type[ExecutionInputType]]`
- **Description**: Input schema class used for validation and JSON Schema generation; defaults to base `ExecutionInputType`

#### `VALIDATORS`
- **Type**: `ClassVar[list[type[BaseExecutionValidator]]]`
- **Description**: Ordered list of validator classes applied after each `execute()` call; defaults to `[IsValidJsonValidator]`

#### `MAX_RETRIES`
- **Type**: `ClassVar[int]`
- **Description**: Maximum validator-feedback correction cycles before giving up; default `3`

#### `FAILURE_CODES`
- **Type**: `ClassVar[type[ExecutionFailureCode]]`
- **Description**: Failure code enum for this definition; override with a subclass to expose execution-specific codes alongside the base ones

**Methods:**

**`execute(input_data, conversation) -> str` (abstract)**: Performs one attempt and returns the raw LLM response string. The base `run()` loop calls this repeatedly until all validators pass or retries are exhausted.

**`run(input_data, conversation) -> ExecutionResult` (concrete)**: Orchestrates the retry loop:
1. Calls `execute()` to get the LLM response
2. Runs each validator in order; the first failure drives what happens next
3. All pass → returns `ExecutionResult(success=True, output=...)`
4. `retry_needed=False` → returns immediately with `validation_failed`
5. `retry_needed=True` with retries remaining → clears `tool_scratchpad`, sends feedback, retries
6. Retries exhausted → asks the LLM for a failure summary and returns `max_retries_exceeded`

## Agent Config Provider

### `ConfigType`

`StrEnum` controlling which system prompt an agent uses:

- **`ConfigType.CONVERSATION`**: Used during regular user-facing conversations
- **`ConfigType.AGENTIC_EXECUTION_DEFINITION`**: Used during autonomous agentic execution runs

### `BaseAgentConfigProvider`

ABC exported from each agent plugin. The `AgentRegistry` calls `get_config(config_type)` to obtain the appropriate `AgentConfig` for the current context.

```python
class BaseAgentConfigProvider(ABC):
    @abstractmethod
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfig:
        ...
```

Plugins that need a different prompt for execution runs implement the branching in `get_config()`. Plugins that always use the same prompt can ignore `config_type`.

