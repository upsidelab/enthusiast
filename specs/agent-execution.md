# Agent Execution — Feature Spec

> **Ticket**: ENT-236
> **Status**: Planning
> **Date**: 2026-03-04

---

## 1. Overview

Agent Execution introduces **agentic execution** as a first-class concept, distinct from the existing conversation-based agent flow. Where conversations are interactive (user ↔ agent), executions are **autonomous, programmatic LLM-driven batch jobs**: submitted via API, the LLM agent runs to completion without user interaction, and the caller inspects the result afterward.

Each execution is tightly coupled to an existing, configured `Agent` instance. This is deliberate — an `Agent` already carries the dataset association, LLM provider choice, system prompt, and tool configuration needed to run. The execution wrapper handles everything the agent normally needs from a conversation — message management, tool call loops, response processing — so the caller only needs to provide structured input and wait for a structured output. There is no human in the loop.

The execution type is **derived from the agent's key** (e.g. an agent with key `catalog-enrichment` maps to `CatalogEnrichmentExecution`). Because multiple agents of the same type can exist on the same dataset, the `Agent` FK is the canonical identifier — passing `execution_type` directly is intentionally not supported.

During the execution run, the plugin creates a `Conversation` internally to drive the agent's message loop. This conversation ID is stored on the record once created, making it inspectable after the fact.

### Goals

- Trigger long-running LLM agent jobs programmatically ("fire and forget").
- Track the full execution lifecycle: `pending → in_progress → finished | failed`.
- Support a **pluggable validator** that the execution consults to decide whether to continue.
- Persist execution history with timing, status, result, and a human-readable summary.
- Expose the above through a REST API and a frontend history/launch view.
- Follow the existing plugin architecture — concrete execution logic lives in agent plugins, shared interfaces live in `enthusiast-common`, and the server discovers available executions via `settings.AVAILABLE_AGENT_EXECUTIONS`.

### Non-Goals (for this iteration)

- Real-time streaming of intermediate execution steps to the browser.
- Chaining executions into pipelines.
- Execution scheduling / cron triggering.

---

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
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  plugins/enthusiast-agent-catalog-enrichment  (example)                │
│    CatalogEnrichmentExecution  (BaseAgentExecution)                    │
│    CatalogEnrichmentExecutionInput  (ExecutionInputType)               │
│    ProductUpsertTracker (BaseExecutionValidator)                       │
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

### `BaseAgentExecution`
The base class carries a concrete `run()` that implements the **validator retry loop**, and an abstract `execute()` that subclasses fill in with the actual single-attempt logic.

**Class-level declarations:**
- `EXECUTION_KEY: ClassVar[str]` — unique slug
- `AGENT_KEY: ClassVar[str]` — must match the `AGENT_KEY` of the agent plugin this execution targets
- `NAME: ClassVar[str]` — human-readable UI label
- `INPUT_TYPE: ClassVar[type[ExecutionInputType]]` — defaults to base `ExecutionInputType`
- `VALIDATORS: ClassVar[list[type[BaseExecutionValidator]]]` — ordered list of validator classes applied after each `execute()` call; defaults to `[IsValidJsonValidator]`
- `MAX_RETRIES: ClassVar[int] = 3` — maximum number of validator-feedback correction cycles before giving up
- `FAILURE_CODES: ClassVar[type[ExecutionFailureCode]]` — the failure code enum for this execution class; defaults to `ExecutionFailureCode`. Override with a subclass to expose domain-specific codes alongside the base ones.

**`execute(input_data, conversation) -> str` (abstract):** performs one attempt at the execution task and returns the raw LLM response string. The base `run()` loop calls this repeatedly until all validators pass or retries are exhausted.

**`run(input_data, agent_execution) -> ExecutionResult` (concrete):** orchestrates the retry loop:
1. Creates a `Conversation` internally via `ConversationManager` and stores it on `agent_execution.conversation`
2. Calls `execute(input_data, conversation)` to get the LLM response string
3. Runs each validator in `VALIDATORS` in order; if any returns a feedback string, sends it to the conversation and calls `execute()` again (up to `MAX_RETRIES` times)
4. If all validators pass → returns `ExecutionResult(success=True, output=...)`
5. If `MAX_RETRIES` is exhausted → sends a final prompt asking the LLM for a succinct failure summary, then returns `ExecutionResult(success=False, failure_code=FAILURE_CODES.MAX_RETRIES_EXCEEDED, failure_summary=<LLM response>)`

No exceptions are raised for expected execution failures — all outcomes (including validator exhaustion) are expressed through `ExecutionResult`. Unexpected errors (programming errors, network failures) are not caught and propagate naturally; the server task's `on_failure` hook catches them and sets `failure_code=ExecutionFailureCode.RUNTIME_ERROR` on the record.

---

## 4. Server-side Implementation

### Django Model — `AgentExecution`

| Field | Type | Notes |
|-------|------|-------|
| `agent` | ForeignKey → `Agent` | Non-nullable; the configured agent this execution runs against. Execution type is derived from `agent.agent_key`. |
| `conversation` | ForeignKey → `Conversation` (nullable) | Created by the plugin during `run()`; populated once the conversation exists |
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

Mirrors `AgentRegistry`. Reads `settings.AVAILABLE_AGENT_EXECUTIONS` (dotted import paths, consistent with `AVAILABLE_AGENTS`), imports each class dynamically, and exposes `get_all()` and `get_by_key(key)`.

The key used for lookup is `agent.agent_key` — the same slug that the agent plugin declares as `AGENT_KEY`.

### Celery Task — `run_agent_execution_task`

1. Load record (with `select_related("agent")`) → `mark_in_progress()`
2. Resolve execution class via `AgentExecutionRegistry.get_by_agent_type(execution.agent.agent_type)`
3. Instantiate, deserialise `execution.input` into `INPUT_TYPE`, call `run(input_data, agent_execution)`
4. If `result.success` → `mark_finished(result.output)`
5. If `not result.success` → `mark_failed(failure_code="max_retries_exceeded", failure_explanation=result.failure_summary)`

The task has no try/except around the execution call. Expected failures (validator exhaustion, invalid LLM response) are communicated through `ExecutionResult` — the task inspects `result.success` and branches accordingly. Unexpected errors propagate naturally to Celery, which marks the task as failed.

`max_retries=0` — no Celery-level retries; resilience is entirely the execution loop's own responsibility.

### REST API

The POST endpoint is nested under `/api/agents/` following the existing convention for child resources (e.g. `api/data_sets/<id>/products`, `api/data_sets/<id>/users`). Read endpoints remain at the flat `/api/agent-executions/` collection, again consistent with how conversations are a flat collection despite belonging to a dataset.

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/agent-executions/` | Paginated execution history (newest first, 25/page). Supports `?agent_id=` filter. |
| POST | `/api/agents/<int:agent_id>/executions/` | Start a new execution for the given agent |
| GET | `/api/agent-executions/<int:pk>/` | Fetch a single execution (used for polling) |

**POST `api/agents/<agent_id>/executions/`**: resolves the agent, derives the execution class from `agent.agent_key`, validates the request body (`input` dict) against the matching `ExecutionInputType`, creates the record, and enqueues the Celery task. Returns 404 if the agent does not exist, 400 if the agent type has no registered execution class or if `input` fails validation.

There is no separate "list types" endpoint. The frontend derives the available input schema by resolving the agent's key against the execution registry — this is done at the API level and returned as `input_schema` on the agent detail response, or fetched on demand before rendering the launch form.

### Hiding Execution Conversations from the Conversation History

Conversations created internally by an execution are implementation details — they represent the agent's internal message loop, not a user-initiated dialogue. Returning them in the standard `GET /api/conversations/` response would clutter the agent history UI with entries the user never started.

**Approach**: `AgentExecution` holds a nullable FK to `Conversation`. The `ConversationListView` queryset is updated to exclude conversations that are referenced by any `AgentExecution` record:

```python
queryset = queryset.exclude(agentexecution__isnull=False)
```

No new field is added to `Conversation` — the reverse relation from `AgentExecution.conversation` is sufficient. This means the exclusion is implicit and automatic: as soon as an execution links its conversation, it disappears from the standard history.

The conversation remains accessible directly via `GET /api/conversations/<id>/` (e.g. for debugging or admin inspection) and is surfaced in context through the execution detail response which includes the `conversation_id`.

### File Map

```
server/agent/
├── models/agent_execution.py     ← NEW
├── serializers/agent_execution.py ← NEW
├── tasks.py                       ← updated
└── execution/
    ├── registry.py                ← NEW
    ├── views.py                   ← NEW
    ├── urls.py                    ← NEW
    └── tests/
        ├── test_registry.py
        ├── test_views.py
        └── test_task.py
```

---

## 5. Plugin Implementation — Catalog Enrichment (example)

The catalog enrichment plugin is the reference implementation. The existing `CatalogEnrichmentAgent` is driven internally.

**`CatalogEnrichmentExecutionInput`** (`ExecutionInputType` subclass): field `max_failures: int` (default 5). The dataset is not part of the input — it is derived from `agent.data_set` at runtime.

**`CatalogEnrichmentExecution`** (`BaseAgentExecution`):
- `EXECUTION_KEY = "catalog-enrichment"`, `AGENT_KEY = "enthusiast-agent-catalog-enrichment"`
- `VALIDATORS = [IsValidJsonValidator, ProductUpsertValidator]` — first checks structural JSON validity, then domain-level validity
- `execute(input_data, conversation)` — iterates over all products in the agent's dataset, drives `CatalogEnrichmentAgent` per product (full LLM loop, no user interaction), uses `ProductUpsertTracker` to stop early on too many failures, returns the final LLM response string for the batch

**`ProductUpsertTracker`** (`BaseExecutionValidator`): validates that the LLM response represents a successful upsert; returns a feedback message string if failures exceed `max_failures`, `None` otherwise.

---

## 6. Frontend

Three routes added to the authenticated router in `frontend/src/main.tsx`:

| Path | Component | Purpose |
|------|-----------|---------|
| `/agent-executions` | `AgentExecutionsPage` | History table + "New execution" button |
| `/agent-executions/new` | `NewAgentExecutionPage` | Select agent (filtered to those with a registered execution class), fill input form, submit |
| `/agent-executions/:id` | `AgentExecutionDetailPage` | Status polling + result/failure display, link to the created conversation |

API client (`frontend/src/lib/api/agent-executions.ts`) exposes `list(filters?)`, `get(id)`, `start(agentId, input)` and is integrated into `ApiClient` via `agentExecutions()`.

`NewAgentExecutionPage` first renders an agent selector (only agents whose `agent_key` maps to a registered execution class are shown). Once an agent is selected, it fetches the `input_schema` and renders a dynamic form (React Hook Form + Zod). `AgentExecutionDetailPage` polls every 3 seconds while `pending` or `in_progress` and links to the execution's conversation when available.

---

## 7. Testing

**`test_registry.py`**: `get_all()`, `get_by_agent_type()` happy path, `get_by_agent_type()` raises `KeyError` for unknown type.

**`test_task.py`**: `pending → in_progress → finished` when `result.success=True`; `pending → in_progress → failed` when `result.success=False` with `failure_summary` stored; unexpected exception propagates without calling `mark_finished`.

**`test_views.py`**: valid start (202); unknown agent (404); soft-deleted agent (404); agent type has no execution class (400); invalid input (400, no record created); list (200); list ordered newest first; get (200); get missing (404); execution conversation excluded from conversation list; execution conversation accessible via detail endpoint.

**`test_is_valid_json_validator.py`**: valid JSON returns `None`; invalid JSON returns the feedback string.

**`test_base_agent_execution.py`**: all validators pass on first attempt → `ExecutionResult(success=True)`; one validator fails → feedback sent to conversation and `execute()` retried; `MAX_RETRIES` exhausted → failure summary requested from LLM → `ExecutionResult(success=False, failure_summary=...)`.

**`test_product_upsert_tracker.py`**: returns `None` below failure threshold; returns feedback string at/above threshold.

**`test_catalog_enrichment_execution.py`**: stops early when `ProductUpsertTracker` signals failure; correct counts in `ExecutionResult.output`; conversation FK is populated after `run()`.

---

## 8. Implementation Order

1. **enthusiast-common** — core interfaces (`BaseAgentExecution`, `BaseExecutionValidator`, `ExecutionResult`, `ExecutionStatus`, `ExecutionInputType`)
2. **Server: Model + Migration** — `agent` FK, nullable `conversation` FK, drop `execution_type`
3. **Server: Registry + Settings key**
4. **Server: Celery Task**
5. **Server: Serializers + Views + URLs**
6. **Server: Tests**
7. **Plugin: CatalogEnrichmentExecution** — implementation, registration, plugin tests
8. **Frontend: API Client**
9. **Frontend: Pages & Components**
