# Agentic Execution — Feature Spec

## 1. Overview

Agentic Execution introduces **agentic execution** as a first-class concept, distinct from the existing conversation-based agent flow. Where conversations are interactive (user ↔ agent), executions are **autonomous, programmatic LLM-driven batch jobs**: submitted via API, the LLM agent runs to completion without user interaction, and the caller inspects the result afterward.

Each execution is tightly coupled to an existing, configured `Agent` instance. This is deliberate — an `Agent` already carries the dataset association, system prompt, and tool configuration needed to run. The execution wrapper handles everything the agent normally needs from a conversation — message management, tool call loops, response processing — so the caller only needs to provide structured input and wait for a structured output. There is no human in the loop.

A single agent plugin can register **multiple agentic execution definition classes**, each with a distinct `EXECUTION_KEY` and all sharing the same `AGENT_KEY`. The caller selects which execution type to run by passing `execution_key` in the POST body. This allows, for example, a catalog enrichment agent to expose separate executions for different enrichment strategies. The `execution_key` is persisted on the `AgenticExecution` record so the Celery task can always resolve the correct class regardless of later registry changes.

During the execution run, the plugin creates a `Conversation` internally to drive the agent's message loop. This conversation ID is stored on the record once created, making it inspectable after the fact.

### Goals

- Trigger long-running LLM agent jobs programmatically ("fire and forget").
- Track the full execution lifecycle: `pending → in_progress → finished | failed`.
- Support **pluggable validators** that the execution consults to decide whether to continue.
- Persist execution history with timing, status, result, and a human-readable summary.
- Expose the above through a REST API and a frontend history/launch view.
- Follow the existing plugin architecture — concrete execution logic lives in agent plugins, shared interfaces live in `enthusiast-common`, and the server discovers available agentic execution definitions via `settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS`.

## 2. Architecture

The diagram below shows the full system with the catalog enrichment plugin as a **concrete example**. The `enthusiast-common` layer defines the abstract interfaces only — any agent plugin can provide its own `BaseAgenticExecutionDefinition` subclass and `ExecutionInputType` following the same pattern.

```
┌────────────────────────────────────────────────────────────────────────┐
│  plugins/enthusiast-common                                             │
│    BaseAgenticExecutionDefinition (ABC)                                │
│    BaseExecutionValidator (ABC)                                        │
│    ExecutionResult (dataclass)                                         │
│    ExecutionStatus (Enum)                                              │
│    ExecutionInputType (Pydantic BaseModel — subclassed per plugin)     │
│    BaseAgentConfigProvider (ABC)  ← agent config interface             │
│    ConfigType (StrEnum)           ← "conversation" | "agentic_execution_definition" │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  plugins/enthusiast-agent-catalog-enrichment  (example)                │
│    CatalogEnrichmentAgenticExecutionDefinition  (BaseAgenticExecutionDefinition)  │
│    CatalogEnrichmentAgenticExecutionInput  (ExecutionInputType)        │
│    CatalogEnrichmentConfigProvider (BaseAgentConfigProvider)           │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  server/                                                               │
│    AgenticExecution (Django model)                                     │
│    AgenticExecutionDefinitionRegistry  ←── settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS │
│    run_agentic_execution_task (Celery)                                 │
│    REST API: /api/agents/{agent_id}/agentic-executions/                │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  frontend/                                                             │
│    /agentic-executions  (history list + launch)                        │
│    /agentic-executions/new  (launch form)                              │
│    /agentic-executions/:id  (detail / status polling)                  │
└────────────────────────────────────────────────────────────────────────┘
```

The pattern mirrors how agents are handled:
- `settings.AVAILABLE_AGENTS` → `AgentRegistry` → `AgentBuilder` → `BaseAgent`
- `settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS` → `AgenticExecutionDefinitionRegistry` → `BaseAgenticExecutionDefinition`

---

## 3. enthusiast-common — New module: `enthusiast_common/agentic_execution/`

### `ExecutionStatus`
Enum: `PENDING`, `IN_PROGRESS`, `FINISHED`, `FAILED`.

### `ExecutionFailureCode`
`StrEnum` that defines standardised failure codes stored on `AgenticExecution.failure_code`. Defined in `enthusiast_common/agentic_execution/errors.py` and attached to `BaseAgenticExecutionDefinition` via `FAILURE_CODES`. The two base codes are:

| Code | Set by | Meaning |
|------|--------|---------|
| `runtime_error` | `MarkExecutionFailedOnErrorTask.on_failure` | Unexpected exception escaped the execution |
| `max_retries_exceeded` | `BaseAgenticExecutionDefinition.run()` | LLM failed to pass validators after `MAX_RETRIES` correction cycles |
| `validation_failed` | `BaseAgenticExecutionDefinition.run()` | A validator rejected the response and set `retry_needed=False` — retrying is not useful |
| `unknown` | Celery task | Execution reported failure but returned no failure code |

Plugins extend this enum to add domain-specific codes and point `FAILURE_CODES` at the subclass::

```python
from enthusiast_common.agentic_execution import ExecutionFailureCode

class CatalogEnrichmentFailureCode(ExecutionFailureCode):
    TOO_MANY_UPSERT_FAILURES = "too_many_upsert_failures"

class CatalogEnrichmentAgenticExecutionDefinition(BaseAgenticExecutionDefinition):
    FAILURE_CODES = CatalogEnrichmentFailureCode
    ...
```

### `ExecutionResult`
Dataclass returned by `BaseAgenticExecutionDefinition.run()`. Fields:
- `success: bool` — whether the execution completed successfully
- `output: dict` — structured output payload (meaningful only when `success=True`)
- `failure_code: ExecutionFailureCode | None` — standardised failure code (set when `success=False`; plugins may use a subclass of `ExecutionFailureCode` for domain-specific codes)
- `failure_summary: str | None` — LLM-generated plain-language explanation of what went wrong (set when `success=False`)

### `ExecutionInputType`
Pydantic `BaseModel` subclassed per plugin to declare and validate structured execution input. The server derives the JSON Schema from it for API responses and request validation.

### `ToolResultMemory`
A dict-based store that tools write to and validators read from during a single execution attempt. One instance is created per `ExecutionConversation` and flows through the injector to tools and through `BaseAgenticExecutionDefinition.run()` to validators.

- `record(tool_name, result)` — stores `result` under `tool_name`, overwriting any previous entry.
- `get_tool_result(tool_name) -> Any | None` — returns the stored value, or `None` if the tool never recorded anything.
- `clear()` — discards all entries; called by `run()` before each retry so validators always see results from the current attempt only.

Each tool–validator pair shares a typed contract via a type alias exported from the tool module (e.g. `UpsertMemoryEntry = dict[str, bool]`). The framework records nothing automatically — tools opt in by calling `record()` in their `run()` method.

### `ValidatorResponse`
Structured return value from `BaseExecutionValidator.validate()`. Fields:
- `validation_successful: bool` — whether the response passed this validator.
- `retry_needed: bool` — whether the run loop should retry after a failure (default `True`). Set to `False` when retrying is pointless — e.g. an external system is unreachable and the LLM cannot fix that by producing a different response. Ignored when `validation_successful` is `True`.
- `feedback: str | None` — plain-language message sent back to the LLM when `retry_needed=True`; used directly as `failure_summary` when `retry_needed=False`.

### `BaseExecutionValidator`
ABC for response validators. A validator inspects the raw string response produced by a single `execute()` call and returns a `ValidatorResponse` that tells the run loop what to do next.

```python
class BaseExecutionValidator(ABC):
    def validate(
        self,
        response: str,
        execution_input: ExecutionInputType,
        tool_result_memory: Optional[ToolResultMemory] = None,
    ) -> ValidatorResponse:
        """Inspect the LLM response and return a structured result."""
```

`tool_result_memory` gives validators access to what tools explicitly recorded during the attempt — not just the final LLM text. Validators that only inspect the response text can ignore it.

The run loop processes the first failing `ValidatorResponse` it encounters:
- All validators return `validation_successful=True` → execution succeeds.
- `validation_successful=False, retry_needed=True` → `feedback` is sent back to the LLM and the attempt is retried (up to `MAX_RETRIES` times).
- `validation_successful=False, retry_needed=False` → the loop stops immediately without retrying; `failure_code` is set to `VALIDATION_FAILED` and `feedback` is used as the `failure_summary`.

Two concrete validators are provided in `enthusiast-common` out of the box:

**`IsValidJsonValidator`** — attempts `json.loads(response)`; if it raises, returns `validation_successful=False`, `retry_needed=True`, feedback `"The response is not valid JSON. Please return the same data as a valid JSON object."`.

**`StopExecutionValidator`** — reads `ToolResultMemory` for the `"stop_execution"` tool name. If the agent called the stop execution tool during the attempt, returns `validation_successful=False`, `retry_needed=False`, with the recorded stop reason as `feedback`. Designed to be placed first in the `VALIDATORS` list so it short-circuits before any other checks.

Plugins can define their own validators (e.g. schema-specific checks, business rule assertions, external system reachability) and attach them via `VALIDATORS`.

### `ConfigType` and `BaseAgentConfigProvider`

Agent plugins may need a different system prompt for agentic execution runs than the one used in interactive conversations — one that drops conversational scaffolding and focuses the LLM entirely on the batch task at hand.

This is handled through the **agent config provider** interface, which lives in `enthusiast_common/agents/config.py` and is separate from `agentic_execution/`.

**`ConfigType`** is a `StrEnum` with two members:

| Member | Value | Used when |
|--------|-------|-----------|
| `ConfigType.CONVERSATION` | `"conversation"` | Regular user-facing conversation |
| `ConfigType.AGENTIC_EXECUTION_DEFINITION` | `"agentic_execution_definition"` | Autonomous agentic execution run |

**`BaseAgentConfigProvider`** is an ABC that each agent plugin exports from its `__init__.py`. The `AgentRegistry` discovers the subclass at runtime by inspecting the plugin module and calls `get_config(config_type)` to obtain the appropriate `AgentConfig`.

```python
class BaseAgentConfigProvider(ABC):
    @abstractmethod
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfig:
        ...
```

Plugins that do not need context-specific behaviour can ignore the `config_type` argument and always return the same configuration. Plugins that do need a different execution prompt implement the branching in `get_config()`:

```python
class MyAgentConfigProvider(BaseAgentConfigProvider):
    def get_config(self, config_type: ConfigType = ConfigType.CONVERSATION) -> AgentConfigWithDefaults:
        system_prompt = EXECUTION_PROMPT if config_type == ConfigType.AGENTIC_EXECUTION_DEFINITION else CONVERSATION_PROMPT
        return AgentConfigWithDefaults(prompt_template=..., ...)
```

The `config_type` flows from `ExecutionConversation` (hardcoded to `ConfigType.AGENTIC_EXECUTION_DEFINITION`) through `ConversationManager.get_answer()` and `AgentRegistry.get_conversation_agent()` to the config provider. Regular conversation calls default to `ConfigType.CONVERSATION` and the provider is invoked with that value.

### `BaseAgenticExecutionDefinition`
The base class carries a concrete `run()` that implements the **validator retry loop**, and an abstract `execute()` that subclasses fill in with the actual single-attempt logic.

**Class-level declarations:**
- `EXECUTION_KEY: ClassVar[str]` — unique slug used to identify and persist this execution type
- `AGENT_KEY: ClassVar[str]` — must match the `AGENT_KEY` of the agent plugin this execution targets; multiple execution definition classes may share the same `AGENT_KEY`
- `NAME: ClassVar[str]` — human-readable UI label
- `DESCRIPTION: ClassVar[Optional[str]]` — optional longer description shown in the execution type selector (defaults to `None`)
- `INPUT_TYPE: ClassVar[type[ExecutionInputType]]` — defaults to base `ExecutionInputType`
- `VALIDATORS: ClassVar[list[type[BaseExecutionValidator]]]` — ordered list of validator classes applied after each `execute()` call; defaults to `[IsValidJsonValidator]`
- `MAX_RETRIES: ClassVar[int] = 3` — maximum number of validator-feedback correction cycles before giving up
- `FAILURE_CODES: ClassVar[type[ExecutionFailureCode]]` — the failure code enum for this execution definition class; defaults to `ExecutionFailureCode`. Override with a subclass to expose domain-specific codes alongside the base ones.

**`ExecutionConversationInterface`** is a `Protocol` that the server implements. It exposes two members:
- `ask(message) -> str` — appends a user message, runs the full agent turn, and returns the agent's final text response.
- `tool_result_memory: ToolResultMemory` — the shared memory instance that tools write to during `ask()`. `run()` passes this to validators after each `execute()` call and clears it before each retry.

**`execute(input_data, conversation) -> str` (abstract):** performs one attempt at the execution task and returns the raw LLM response string. The base `run()` loop calls this repeatedly until all validators pass or retries are exhausted.

**`run(input_data, conversation) -> ExecutionResult` (concrete):** orchestrates the retry loop:
1. Calls `execute(input_data, conversation)` to get the LLM response string
2. Runs each validator in `VALIDATORS` in order, passing `execution_input` and `conversation.tool_result_memory`; the first failing `ValidatorResponse` drives the next step:
   - All pass → returns `ExecutionResult(success=True, output=...)`
   - `retry_needed=False` → returns immediately with `failure_code=VALIDATION_FAILED` and the validator's `feedback` as `failure_summary` (no additional LLM call)
   - `retry_needed=True` and retries remain → clears `tool_result_memory`, sends `feedback` to the conversation, and calls `execute()` again
3. If `MAX_RETRIES` is exhausted → sends a final prompt asking the LLM for a succinct failure summary, then returns `ExecutionResult(success=False, failure_code=FAILURE_CODES.MAX_RETRIES_EXCEEDED, failure_summary=<LLM response>)`

No exceptions are raised for expected execution failures — all outcomes (including validator exhaustion) are expressed through `ExecutionResult`. Unexpected errors (programming errors, network failures) are not caught and propagate naturally; the server task's `on_failure` hook catches them and sets `failure_code=ExecutionFailureCode.RUNTIME_ERROR` on the record.

---

## 4. Server-side Implementation

### Django Model — `AgenticExecution`

| Field | Type | Notes |
|-------|------|-------|
| `agent` | ForeignKey → `Agent` | Non-nullable; the configured agent this execution runs against. |
| `execution_key` | CharField | `EXECUTION_KEY` of the execution definition class selected at creation time. Persisted so the Celery task can resolve the correct class via `AgenticExecutionDefinitionRegistry.get_by_key()`. |
| `conversation` | ForeignKey → `Conversation` | Always created by the view before the task is enqueued |
| `status` | CharField | `pending \| in_progress \| finished \| failed` |
| `input` | JSONField | Input payload validated against `ExecutionInputType` at request time |
| `result` | JSONField (nullable) | Output from `ExecutionResult.output` (set on finish) |
| `failure_code` | CharField (nullable) | Standardized error code (set on failure) |
| `failure_explanation` | TextField (nullable) | LLM-generated explanation of what went wrong (set on failure) |
| `celery_task_id` | CharField (nullable) | ID of the Celery task running this execution |
| `started_at` | DateTimeField | Auto-set on creation |
| `finished_at` | DateTimeField (nullable) | Set when reaching a terminal state |

Computed property `duration_seconds`. Helper methods: `mark_in_progress()`, `mark_finished()`, `mark_failed(failure_code, failure_explanation)`.

### Registry — `AgenticExecutionDefinitionRegistry`

Mirrors `AgentRegistry`. Reads `settings.AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS` (dotted import paths, consistent with `AVAILABLE_AGENTS`), imports each class dynamically, and exposes:

- `get_all()` — all registered agentic execution definition classes
- `get_by_key(key)` — returns the single class with the matching `EXECUTION_KEY`; raises `KeyError` if not found
- `get_by_agent_type(agent_type)` — returns a **list** of all execution definition classes whose `AGENT_KEY` matches; returns an empty list if none are registered

### Celery Task — `run_agentic_execution_task`

1. Load record (with `select_related("agent")`) → `mark_in_progress()`
2. Resolve execution definition class via `AgenticExecutionDefinitionRegistry.get_by_key(execution.execution_key)`
3. Instantiate, deserialise `execution.input` into `INPUT_TYPE`, call `run(input_data, conversation)`
4. If `result.success` → `mark_finished(result.output)`
5. If `not result.success` → `mark_failed(failure_code=result.failure_code or "unknown", failure_explanation=result.failure_summary)`

The `Conversation` is always created by the view before the task is enqueued — the task reads it directly from `execution.conversation` and never creates one itself.

The task has no try/except around the execution call. Expected failures (validator exhaustion, invalid LLM response) are communicated through `ExecutionResult` — the task inspects `result.success` and branches accordingly. Unexpected errors propagate naturally to Celery, which marks the task as failed.

`max_retries=0` — no Celery-level retries; resilience is entirely the execution loop's own responsibility.

### Conversation Creation

The `Conversation` is always created synchronously during the API request — before the Celery task is enqueued. `AgenticExecution.conversation` is therefore non-nullable and always populated by the time the task runs.

### File Upload

When an agent's `file_upload` flag is `True`, the agentic execution API accepts files alongside the input payload via `multipart/form-data`. Files are parsed and stored synchronously during the request, attached to the conversation that is created at the same time. The Celery task then runs against an already-populated conversation and requires no knowledge of files — the agent's file tools discover them through the conversation as normal.

Sending files to an agent with `file_upload=False` returns a 400. Unsupported file types are also rejected with a 400 before any records are created.

The `input` payload is a JSON-encoded string when sent as part of multipart form data; the serializer handles the decoding transparently so the rest of the pipeline is unaffected.

### REST API

The POST endpoint is nested under `/api/agents/` following the existing convention for child resources (e.g. `api/data_sets/<id>/products`, `api/data_sets/<id>/users`). Read endpoints remain at the flat `/api/agentic-executions/` collection, again consistent with how conversations are a flat collection despite belonging to a dataset.

| Method | URL | Description                                                                                                        |
|--------|-----|--------------------------------------------------------------------------------------------------------------------|
| GET | `/api/agents/<int:agent_id>/agentic-execution-definitions/` | List all agentic execution definitions registered for this agent (key, name, description, input_schema).      |
| POST | `/api/agents/<int:agent_id>/agentic-executions/` | Start a new agentic execution for the given agent. Accepts `application/json` or `multipart/form-data`.            |
| GET | `/api/agentic-executions/` | Paginated execution history (newest first, 25/page). Supports `?agent_id=`, `?status=` and `?dataset_id=` filters. |
| GET | `/api/agentic-executions/<int:pk>/` | Fetch a single agentic execution (used for polling)                                                                |

**GET `api/agents/<agent_id>/agentic-execution-definitions/`**: returns a list of `{key, name, description, input_schema}` objects for all agentic execution definition classes registered for the agent's type. The frontend calls this when rendering the launch form to populate the execution type selector and derive the dynamic input form from `input_schema`. Returns 404 if the agent does not exist; returns an empty list if no execution definition classes are registered.

**POST `api/agents/<agent_id>/agentic-executions/`**: resolves the agent, uses the `execution_key` field from the request body to look up the execution definition class (via `get_by_key()`), validates that the class belongs to the agent's type, validates `input` against the matching `ExecutionInputType`, optionally processes uploaded files, creates the record (persisting `execution_key`), and enqueues the Celery task. Returns 404 if the agent does not exist; 400 if `execution_key` is unknown or belongs to a different agent type, if `input` fails validation, or if files are sent to an agent with `file_upload=False`.

### Hiding Execution Conversations from the Conversation History

Conversations created internally by an agentic execution are implementation details — they represent the agent's internal message loop, not a user-initiated dialogue. Returning them in the standard `GET /api/conversations/` response would clutter the agent history UI with entries the user never started.

**Approach**: `AgenticExecution` holds a FK to `Conversation`. The `ConversationListView` queryset is updated to exclude conversations that are referenced by any `AgenticExecution` record:

```python
queryset = queryset.exclude(agentic_execution__isnull=False)
```

No new field is added to `Conversation` — the reverse relation from `AgenticExecution.conversation` is sufficient. This means the exclusion is implicit and automatic: as soon as an execution links its conversation, it disappears from the standard history.

The conversation remains accessible directly via `GET /api/conversations/<id>/` (e.g. for debugging or admin inspection) and is surfaced in context through the execution detail response which includes the `conversation_id`.

### Read-only Enforcement for Execution Conversations

Agentic execution conversations are created by the system, not by the user, and must not receive further user messages. Both the API and the frontend enforce this constraint.

**API**: `ConversationView.post()` (the "ask a question" endpoint) checks whether the conversation is linked to an `AgenticExecution` record via `hasattr(conversation, "agentic_execution")`. If it is, the request is rejected with `400 Conversation locked.` — the same response returned for deleted-agent conversations.

**Serializer**: `ConversationContentSerializer` exposes an `is_execution_conversation: bool` field computed from the `agentic_execution` reverse relation. This lets the frontend determine at render time whether the conversation is read-only without a separate API call.

**Frontend**: When `is_execution_conversation` is `true` on the loaded conversation, `ChatSession` includes it in the `conversationLocked` flag passed to `ChatWindow`. The `MessageComposer` disables the textarea and send button and shows the placeholder "This conversation is read-only." — consistent with the existing locked-conversation behaviour for deleted or corrupted agents.

### File Map

```
server/agent/
├── models/agentic_execution.py      ← NEW
├── serializers/agentic_execution.py ← NEW
└── execution/
    ├── registry.py                ← NEW
    ├── services.py                ← NEW
    ├── tasks.py                   ← NEW
    ├── views.py                   ← NEW
    ├── urls.py                    ← NEW
    └── tests/
        ├── test_services.py
        └── test_views.py
```

---

## 5. Plugin Implementation — Catalog Enrichment (example)

The catalog enrichment plugin is the reference implementation. The existing `CatalogEnrichmentAgent` is driven internally.

**`CatalogEnrichmentConfigProvider`** (`BaseAgentConfigProvider`): exported from the plugin's `__init__.py`. Implements `get_config(config_type)` and returns a different system prompt depending on the context:
- `ConfigType.CONVERSATION` — the standard conversational prompt (`CATALOG_ENRICHMENT_TOOL_CALLING_AGENT_PROMPT`) that includes user-interaction guidance
- `ConfigType.AGENTIC_EXECUTION_DEFINITION` — a stripped-down execution prompt (`CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT`) that drops conversational tone, states the LLM is in a batch pipeline, and mandates a JSON-only response of the form `{"<product identifier>": "<upsert success or failure reason>", ...}`

**`CatalogEnrichmentAgenticExecutionInput`** (`ExecutionInputType` subclass):
- `additional_instructions: Optional[str]` (default `None`) — free-text instructions appended to the default prompt.
- `skus: Optional[list[str]]` (default `None`) — when provided, `AllSkusUpsertedValidator` verifies that every SKU in this list was attempted by the agent. When absent, no SKU coverage check is performed.

The dataset is not part of the input; it is derived from `agent.data_set` at runtime.

**`CatalogEnrichmentAgenticExecutionDefinition`** (`BaseAgenticExecutionDefinition`):
- `EXECUTION_KEY = "catalog-enrichment"`, `AGENT_KEY = "enthusiast-agent-catalog-enrichment"`
- `VALIDATORS = [StopExecutionValidator, IsValidJsonValidator, AllUpsertsSucceededValidator, AllSkusUpsertedValidator]`
- `execute(input_data, conversation)` — sends a single message to the agent (the `additional_instructions` value, or a default prompt when absent) and returns its raw response string. The agent's tool stack handles the actual product enrichment within that turn.

**`StopExecutionTool`** — an `LLMTool` that lives in the catalog enrichment plugin and is attached to the agent only during agentic execution conversations (via `CatalogEnrichmentConfigProvider`). The agent calls it with a `stop_reason` string when further progress is impossible (e.g. required data absent from all sources, no eCommerce connector configured). Records the reason to `ToolResultMemory`; `StopExecutionValidator` reads it and halts the run without retry.

**`AllUpsertsSucceededValidator`** — reads the `UpsertMemoryEntry` (`dict[str, bool]`) recorded by `UpsertProductDetailsTool`. Any `False` value triggers a retry with the list of failed SKUs as feedback.

**`AllSkusUpsertedValidator`** — active only when `execution_input.skus` is provided. Reads the same `UpsertMemoryEntry` to determine which SKUs were attempted; reports any missing SKUs and asks the agent to locate their data and retry the full upsert. If the data cannot be found, instructs the agent to stop the execution.

---

## 6. Frontend

Two views are added, all dataset-scoped following the `/data-sets/:dataSetId/...` convention. An **Agentic Executions** link is added to the **Configure** section of the sidebar, visible to all authenticated users.

| Path | Purpose |
|------|---------|
| `/data-sets/:dataSetId/agentic-executions` | History dashboard — paginated table filterable by agent and status |
| `/data-sets/:dataSetId/agentic-executions/:executionId` | Detail view — live status polling, result or failure display, link to the execution's conversation |

**History dashboard** lists past agentic executions for the current dataset with agent and status filters. Filter state is kept in URL search params so it survives refresh. A **New Execution** button opens the launch form.

**Launch form** is a modal dialog accessible from the history dashboard. The user selects an agent, then an execution type (populated dynamically based on the chosen agent), provides a JSON input payload, and optionally attaches files (shown only when the selected agent supports file upload). Field-level and general API errors are surfaced inline. On success the user is redirected to the new execution's detail view.

**Detail view** polls the execution status every 3 seconds while the job is running and stops once a terminal state is reached. Finished executions show the structured result; failed executions show the failure code and the LLM-generated explanation. A link to the underlying conversation is always shown, giving visibility into the agent's internal message loop.

---

## 7. Testing

**`test_services.py`**: conversation and execution record created correctly; `execution_key` persisted; Celery task enqueued with execution ID; file upload validation (unsupported extension, non-file-upload agent); file attached as `ConversationFile(is_hidden=False)` with correct category.

**`test_views.py`**: `GET agentic-execution-definitions` — 200 with list, 404 for unknown agent. `POST executions` — 202 on valid start; 404 for unknown or soft-deleted agent; 400 for unknown `execution_key`, mismatched agent type, invalid input, or files sent to a non-file-upload agent. List — 200, ordered newest first, filterable by `agent_id`. Detail — 200, 404 for missing. Agentic execution conversation excluded from the standard conversation list; accessible via the detail endpoint.
