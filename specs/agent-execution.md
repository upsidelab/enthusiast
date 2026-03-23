# Agent Execution — Feature Spec

> **Ticket**: ENT-236
> **Status**: In Progress (backend + catalog enrichment plugin implemented; frontend pending)
> **Date**: 2026-03-04

---

## 1. Overview

Agent Execution introduces **agentic execution** as a first-class concept, distinct from the existing conversation-based agent flow. Where conversations are interactive (user ↔ agent), executions are **autonomous, programmatic LLM-driven batch jobs**: submitted via API, the LLM agent runs to completion without user interaction, and the caller inspects the result afterward.

Each execution is tightly coupled to an existing, configured `Agent` instance. This is deliberate — an `Agent` already carries the dataset association, system prompt, and tool configuration needed to run. The execution wrapper handles everything the agent normally needs from a conversation — message management, tool call loops, response processing — so the caller only needs to provide structured input and wait for a structured output. There is no human in the loop.

A single agent plugin can register **multiple execution classes**, each with a distinct `EXECUTION_KEY` and all sharing the same `AGENT_KEY`. The caller selects which execution type to run by passing `execution_key` in the POST body. This allows, for example, a catalog enrichment agent to expose separate executions for different enrichment strategies. The `execution_key` is persisted on the `AgentExecution` record so the Celery task can always resolve the correct class regardless of later registry changes.

During the execution run, the plugin creates a `Conversation` internally to drive the agent's message loop. This conversation ID is stored on the record once created, making it inspectable after the fact.

### Goals

- Trigger long-running LLM agent jobs programmatically ("fire and forget").
- Track the full execution lifecycle: `pending → in_progress → finished | failed`.
- Support **pluggable validators** that the execution consults to decide whether to continue.
- Persist execution history with timing, status, result, and a human-readable summary.
- Expose the above through a REST API and a frontend history/launch view.
- Follow the existing plugin architecture — concrete execution logic lives in agent plugins, shared interfaces live in `enthusiast-common`, and the server discovers available executions via `settings.AVAILABLE_AGENT_EXECUTIONS`.

## 2. Architecture

The diagram below shows the full system with the catalog enrichment plugin as a **concrete example**. The `enthusiast-common` layer defines the abstract interfaces only — any agent plugin can provide its own `BaseAgentExecution` subclass and `ExecutionInputType` following the same pattern.

```
┌────────────────────────────────────────────────────────────────────────┐
│  plugins/enthusiast-common                                             │
│    BaseAgentExecution (ABC)                                            │
│    BaseExecutionValidator (ABC)                                        │
│    ExecutionResult (dataclass)                                         │
│    ExecutionStatus (Enum)                                              │
│    ExecutionInputType (Pydantic BaseModel — subclassed per plugin)     │
│    BaseAgentConfigProvider (ABC)  ← agent config interface             │
│    ConfigType (StrEnum)           ← "conversation" | "agent_execution" │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  plugins/enthusiast-agent-catalog-enrichment  (example)                │
│    CatalogEnrichmentExecution  (BaseAgentExecution)                    │
│    CatalogEnrichmentExecutionInput  (ExecutionInputType)               │
│    CatalogEnrichmentConfigProvider (BaseAgentConfigProvider)           │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  server/                                                               │
│    AgentExecution (Django model)                                       │
│    AgentExecutionRegistry  ←── settings.AVAILABLE_AGENT_EXECUTIONS     │
│    run_agent_execution_task (Celery)                                   │
│    REST API: /api/agents/{agent_id}/executions/                        │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  frontend/                                                             │
│    /agent-executions  (history list + launch)                          │
│    /agent-executions/new  (launch form)                                │
│    /agent-executions/:id  (detail / status polling)                    │
└────────────────────────────────────────────────────────────────────────┘
```

The pattern mirrors how agents are handled:
- `settings.AVAILABLE_AGENTS` → `AgentRegistry` → `AgentBuilder` → `BaseAgent`
- `settings.AVAILABLE_AGENT_EXECUTIONS` → `AgentExecutionRegistry` → `BaseAgentExecution`

---

## 3. enthusiast-common — New module: `enthusiast_common/agent_execution/`

### `ExecutionStatus`
Enum: `PENDING`, `IN_PROGRESS`, `FINISHED`, `FAILED`.

### `ExecutionFailureCode`
`StrEnum` that defines standardised failure codes stored on `AgentExecution.failure_code`. Defined in `enthusiast_common/agent_execution/errors.py` and attached to `BaseAgentExecution` via `FAILURE_CODES`. The two base codes are:

| Code | Set by | Meaning |
|------|--------|---------|
| `runtime_error` | `MarkExecutionFailedOnErrorTask.on_failure` | Unexpected exception escaped the execution |
| `max_retries_exceeded` | `BaseAgentExecution.run()` | LLM failed to pass validators after `MAX_RETRIES` correction cycles |
| `unknown` | Celery task | Execution reported failure but returned no failure code |

Plugins extend this enum to add domain-specific codes and point `FAILURE_CODES` at the subclass::

```python
from enthusiast_common.agent_execution import ExecutionFailureCode

class CatalogEnrichmentFailureCode(ExecutionFailureCode):
    TOO_MANY_UPSERT_FAILURES = "too_many_upsert_failures"

class CatalogEnrichmentExecution(BaseAgentExecution):
    FAILURE_CODES = CatalogEnrichmentFailureCode
    ...
```

### `ExecutionResult`
Dataclass returned by `BaseAgentExecution.run()`. Fields:
- `success: bool` — whether the execution completed successfully
- `output: dict` — structured output payload (meaningful only when `success=True`)
- `failure_code: ExecutionFailureCode | None` — standardised failure code (set when `success=False`; plugins may use a subclass of `ExecutionFailureCode` for domain-specific codes)
- `failure_summary: str | None` — LLM-generated plain-language explanation of what went wrong (set when `success=False`)

### `ExecutionInputType`
Pydantic `BaseModel` subclassed per plugin to declare and validate structured execution input. The server derives the JSON Schema from it for API responses and request validation.

### `BaseExecutionValidator`
ABC for response validators. A validator inspects the raw string response produced by a single `execute()` call and either approves it or returns a natural-language feedback message that gets forwarded to the LLM for correction.

```python
class BaseExecutionValidator(ABC):
    def validate(self, response: str) -> str | None:
        """Return None if the response is valid, or a feedback string to send back to the LLM."""
```

A concrete validator is provided in `enthusiast-common` out of the box:

**`IsValidJsonValidator`** — attempts `json.loads(response)`; if it raises, returns `"The response is not valid JSON. Please return the same data in valid JSON format."`.

Plugins can define their own validators (e.g. schema-specific checks, business rule assertions) and attach them via `VALIDATORS`.

### `ConfigType` and `BaseAgentConfigProvider`

Agent plugins may need a different system prompt for execution runs than the one used in interactive conversations — one that drops conversational scaffolding and focuses the LLM entirely on the batch task at hand.

This is handled through the **agent config provider** interface, which lives in `enthusiast_common/agents/config.py` and is separate from `agent_execution/`.

**`ConfigType`** is a `StrEnum` with two members:

| Member | Value | Used when |
|--------|-------|-----------|
| `ConfigType.CONVERSATION` | `"conversation"` | Regular user-facing conversation |
| `ConfigType.AGENT_EXECUTION` | `"agent_execution"` | Autonomous batch execution run |

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
        system_prompt = EXECUTION_PROMPT if config_type == ConfigType.AGENT_EXECUTION else CONVERSATION_PROMPT
        return AgentConfigWithDefaults(prompt_template=..., ...)
```

The `config_type` flows from `ExecutionConversation` (hardcoded to `ConfigType.AGENT_EXECUTION`) through `ConversationManager.get_answer()` and `AgentRegistry.get_conversation_agent()` to the config provider. Regular conversation calls default to `ConfigType.CONVERSATION` and the provider is invoked with that value.

### `BaseAgentExecution`
The base class carries a concrete `run()` that implements the **validator retry loop**, and an abstract `execute()` that subclasses fill in with the actual single-attempt logic.

**Class-level declarations:**
- `EXECUTION_KEY: ClassVar[str]` — unique slug used to identify and persist this execution type
- `AGENT_KEY: ClassVar[str]` — must match the `AGENT_KEY` of the agent plugin this execution targets; multiple execution classes may share the same `AGENT_KEY`
- `NAME: ClassVar[str]` — human-readable UI label
- `DESCRIPTION: ClassVar[Optional[str]]` — optional longer description shown in the execution type selector (defaults to `None`)
- `INPUT_TYPE: ClassVar[type[ExecutionInputType]]` — defaults to base `ExecutionInputType`
- `VALIDATORS: ClassVar[list[type[BaseExecutionValidator]]]` — ordered list of validator classes applied after each `execute()` call; defaults to `[IsValidJsonValidator]`
- `MAX_RETRIES: ClassVar[int] = 3` — maximum number of validator-feedback correction cycles before giving up
- `FAILURE_CODES: ClassVar[type[ExecutionFailureCode]]` — the failure code enum for this execution class; defaults to `ExecutionFailureCode`. Override with a subclass to expose domain-specific codes alongside the base ones.

**`execute(input_data, conversation) -> str` (abstract):** performs one attempt at the execution task and returns the raw LLM response string. The base `run()` loop calls this repeatedly until all validators pass or retries are exhausted.

**`run(input_data, conversation) -> ExecutionResult` (concrete):** orchestrates the retry loop:
1. Calls `execute(input_data, conversation)` to get the LLM response string
2. Runs each validator in `VALIDATORS` in order; if any returns a feedback string, sends it to the conversation and calls `execute()` again (up to `MAX_RETRIES` times)
3. If all validators pass → returns `ExecutionResult(success=True, output=...)`
4. If `MAX_RETRIES` is exhausted → sends a final prompt asking the LLM for a succinct failure summary, then returns `ExecutionResult(success=False, failure_code=FAILURE_CODES.MAX_RETRIES_EXCEEDED, failure_summary=<LLM response>)`

No exceptions are raised for expected execution failures — all outcomes (including validator exhaustion) are expressed through `ExecutionResult`. Unexpected errors (programming errors, network failures) are not caught and propagate naturally; the server task's `on_failure` hook catches them and sets `failure_code=ExecutionFailureCode.RUNTIME_ERROR` on the record.

---

## 4. Server-side Implementation

### Django Model — `AgentExecution`

| Field | Type | Notes |
|-------|------|-------|
| `agent` | ForeignKey → `Agent` | Non-nullable; the configured agent this execution runs against. |
| `execution_key` | CharField | `EXECUTION_KEY` of the execution class selected at creation time. Persisted so the Celery task can resolve the correct class via `AgentExecutionRegistry.get_by_key()`. |
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

### Registry — `AgentExecutionRegistry`

Mirrors `AgentRegistry`. Reads `settings.AVAILABLE_AGENT_EXECUTIONS` (dotted import paths, consistent with `AVAILABLE_AGENTS`), imports each class dynamically, and exposes:

- `get_all()` — all registered execution classes
- `get_by_key(key)` — returns the single class with the matching `EXECUTION_KEY`; raises `KeyError` if not found
- `get_by_agent_type(agent_type)` — returns a **list** of all execution classes whose `AGENT_KEY` matches; returns an empty list if none are registered

### Celery Task — `run_agent_execution_task`

1. Load record (with `select_related("agent")`) → `mark_in_progress()`
2. Resolve execution class via `AgentExecutionRegistry.get_by_key(execution.execution_key)`
3. Instantiate, deserialise `execution.input` into `INPUT_TYPE`, call `run(input_data, conversation)`
4. If `result.success` → `mark_finished(result.output)`
5. If `not result.success` → `mark_failed(failure_code=result.failure_code or "unknown", failure_explanation=result.failure_summary)`

The `Conversation` is always created by the view before the task is enqueued — the task reads it directly from `execution.conversation` and never creates one itself.

The task has no try/except around the execution call. Expected failures (validator exhaustion, invalid LLM response) are communicated through `ExecutionResult` — the task inspects `result.success` and branches accordingly. Unexpected errors propagate naturally to Celery, which marks the task as failed.

`max_retries=0` — no Celery-level retries; resilience is entirely the execution loop's own responsibility.

### Conversation Creation

The `Conversation` is always created synchronously during the API request — before the Celery task is enqueued. `AgentExecution.conversation` is therefore non-nullable and always populated by the time the task runs.

### File Upload

When an agent's `file_upload` flag is `True`, the execution API accepts files alongside the input payload via `multipart/form-data`. Files are parsed and stored synchronously during the request, attached to the conversation that is created at the same time. The Celery task then runs against an already-populated conversation and requires no knowledge of files — the agent's file tools discover them through the conversation as normal.

Sending files to an agent with `file_upload=False` returns a 400. Unsupported file types are also rejected with a 400 before any records are created.

The `input` payload is a JSON-encoded string when sent as part of multipart form data; the serializer handles the decoding transparently so the rest of the pipeline is unaffected.

### REST API

The POST endpoint is nested under `/api/agents/` following the existing convention for child resources (e.g. `api/data_sets/<id>/products`, `api/data_sets/<id>/users`). Read endpoints remain at the flat `/api/agent-executions/` collection, again consistent with how conversations are a flat collection despite belonging to a dataset.

| Method | URL | Description                                                                                                        |
|--------|-----|--------------------------------------------------------------------------------------------------------------------|
| GET | `/api/agents/<int:agent_id>/execution-types/` | List all execution types registered for this agent (key, name, description, input_schema).                         |
| POST | `/api/agents/<int:agent_id>/executions/` | Start a new execution for the given agent. Accepts `application/json` or `multipart/form-data`.                    |
| GET | `/api/agent-executions/` | Paginated execution history (newest first, 25/page). Supports `?agent_id=`, `?status=` and `?dataset_id=` filters. |
| GET | `/api/agent-executions/<int:pk>/` | Fetch a single execution (used for polling)                                                                        |

**GET `api/agents/<agent_id>/execution-types/`**: returns a list of `{key, name, description, input_schema}` objects for all execution classes registered for the agent's type. The frontend calls this when rendering the launch form to populate the execution type selector and derive the dynamic input form from `input_schema`. Returns 404 if the agent does not exist; returns an empty list if no execution classes are registered.

**POST `api/agents/<agent_id>/executions/`**: resolves the agent, uses the `execution_key` field from the request body to look up the execution class (via `get_by_key()`), validates that the class belongs to the agent's type, validates `input` against the matching `ExecutionInputType`, optionally processes uploaded files, creates the record (persisting `execution_key`), and enqueues the Celery task. Returns 404 if the agent does not exist; 400 if `execution_key` is unknown or belongs to a different agent type, if `input` fails validation, or if files are sent to an agent with `file_upload=False`.

### Hiding Execution Conversations from the Conversation History

Conversations created internally by an execution are implementation details — they represent the agent's internal message loop, not a user-initiated dialogue. Returning them in the standard `GET /api/conversations/` response would clutter the agent history UI with entries the user never started.

**Approach**: `AgentExecution` holds a FK to `Conversation`. The `ConversationListView` queryset is updated to exclude conversations that are referenced by any `AgentExecution` record:

```python
queryset = queryset.exclude(agent_execution__isnull=False)
```

No new field is added to `Conversation` — the reverse relation from `AgentExecution.conversation` is sufficient. This means the exclusion is implicit and automatic: as soon as an execution links its conversation, it disappears from the standard history.

The conversation remains accessible directly via `GET /api/conversations/<id>/` (e.g. for debugging or admin inspection) and is surfaced in context through the execution detail response which includes the `conversation_id`.

### File Map

```
server/agent/
├── models/agent_execution.py      ← NEW
├── serializers/agent_execution.py ← NEW
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
- `ConfigType.AGENT_EXECUTION` — a stripped-down execution prompt (`CATALOG_ENRICHMENT_EXECUTION_SYSTEM_PROMPT`) that drops conversational tone, states the LLM is in a batch pipeline, and mandates a JSON-only response of the form `{"<product identifier>": "<upsert success or failure reason>", ...}`

**`CatalogEnrichmentExecutionInput`** (`ExecutionInputType` subclass): field `additional_instructions: Optional[str]` (default `None`) — free-text instructions appended to the default prompt. The dataset is not part of the input; it is derived from `agent.data_set` at runtime.

**`CatalogEnrichmentExecution`** (`BaseAgentExecution`):
- `EXECUTION_KEY = "catalog-enrichment"`, `AGENT_KEY = "enthusiast-agent-catalog-enrichment"`
- Uses the default `VALIDATORS = [IsValidJsonValidator]`
- `execute(input_data, conversation)` — sends a single message to the agent (the `additional_instructions` value, or a default prompt when absent) and returns its raw response string. The agent's tool stack (including the product upsert tool) handles the actual product enrichment within that turn.

---

## 6. Frontend

Two views are added, all dataset-scoped following the `/data-sets/:dataSetId/...` convention. An **Executions** link is added to the **Configure** section of the sidebar, visible to all authenticated users. Executions are started programmatically via the REST API — there is no launch form in the UI.

| Path | Purpose |
|------|---------|
| `/data-sets/:dataSetId/agent-executions` | History dashboard — paginated table filterable by agent and status |
| `/data-sets/:dataSetId/agent-executions/:executionId` | Detail view — live status polling, result or failure display, link to the execution's conversation |

**History dashboard** lists past executions for the current dataset with agent and status filters. Filter state is kept in URL search params so it survives refresh.

**Detail view** polls the execution status every 3 seconds while the job is running and stops once a terminal state is reached. Finished executions show the structured result; failed executions show the failure code and the LLM-generated explanation. A link to the underlying conversation is always shown, giving visibility into the agent's internal message loop.

---

## 7. Testing

**`test_services.py`**: conversation and execution record created correctly; `execution_key` persisted; Celery task enqueued with execution ID; file upload validation (unsupported extension, non-file-upload agent); file attached as `ConversationFile(is_hidden=False)` with correct category.

**`test_views.py`**: `GET execution-types` — 200 with list, 404 for unknown agent. `POST executions` — 202 on valid start; 404 for unknown or soft-deleted agent; 400 for unknown `execution_key`, mismatched agent type, invalid input, or files sent to a non-file-upload agent. List — 200, ordered newest first, filterable by `agent_id`. Detail — 200, 404 for missing. Execution conversation excluded from the standard conversation list; accessible via the detail endpoint.
