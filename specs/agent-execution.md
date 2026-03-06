# Agent Execution — Feature Spec

> **Ticket**: ENT-236
> **Status**: Planning
> **Date**: 2026-03-04

---

## 1. Overview

Agent Execution introduces **agentic execution** as a first-class concept, distinct from the existing conversation-based agent flow. Where conversations are interactive (user ↔ agent), executions are **autonomous, programmatic LLM-driven batch jobs**: submitted via API, the LLM agent runs to completion without user interaction, and the caller inspects the result afterward.

Each execution is backed by an existing, configured agent (e.g. `CatalogEnrichmentAgent`). The execution wrapper handles everything the agent normally needs from a conversation — message management, tool call loops, response processing — so the caller only needs to provide structured input and wait for a structured output. There is no human in the loop.

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
│    REST API: /api/agent-executions/                                    │
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

- `ExecutionStatus` — enum: `PENDING`, `IN_PROGRESS`, `FINISHED`, `FAILED`
- `ExecutionResult` — dataclass with output payload, optional summary, and list of non-fatal issue descriptions
- `ExecutionInputType` — Pydantic `BaseModel` subclassed per plugin to declare and validate structured execution input; the server derives the JSON Schema from it for API responses and request validation
- `BaseExecutionValidator` — ABC for pluggable continue/stop strategies; implementations track per-item success/failure rates and expose an issue summary via `should_continue()` and `get_issue_summary()`
- `BaseAgentExecution` — ABC for all agentic executions; subclasses declare `EXECUTION_KEY` (slug), `NAME` (UI label), and optionally a `ExecutionInputType` subclass; must implement `run() -> ExecutionResult`

---

## 4. Server-side Implementation

### Django Model — `AgentExecution`

| Field | Type | Notes |
|-------|------|-------|
| `execution_type` | CharField | `EXECUTION_KEY` of the subclass used |
| `status` | CharField | `pending \| in_progress \| finished \| failed` |
| `input` | JSONField | Input payload validated against `ExecutionInputType` at request time |
| `result` | JSONField (nullable) | Output from `ExecutionResult.output` (set on finish) |
| `failure_code` | CharField (nullable) | Standardized error code (set on failure) |
| `failure_explanation` | TextField (nullable) | LLM-generated explanation of what went wrong (set on failure) |
| `summary` | TextField (nullable) | From `ExecutionResult.summary` or validator issues |
| `celery_task_id` | CharField (nullable) | ID of the Celery task running this execution |
| `started_at` | DateTimeField | Auto-set on creation |
| `finished_at` | DateTimeField (nullable) | Set when reaching a terminal state |

Computed property `duration_seconds`. Helper methods: `mark_in_progress()`, `mark_finished()`, `mark_failed(failure_code, failure_explanation)`.

### Registry — `AgentExecutionRegistry`

Mirrors `AgentRegistry`. Reads `settings.AVAILABLE_AGENT_EXECUTIONS` (dotted import paths, consistent with `AVAILABLE_AGENTS`), imports each class dynamically, and exposes `get_all()` and `get_by_key(key)`.

### Celery Task — `run_agent_execution_task`

1. Load record → `mark_in_progress()`
2. Resolve class via `AgentExecutionRegistry.get_by_key()`
3. Instantiate and call `run()`
4. On success → `mark_finished()`
5. On exception → `mark_failed(failure_code, failure_explanation)`

`max_retries=0` — resilience is the execution's own responsibility.

### REST API

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/agent-executions/types/` | List available types with `ExecutionInputType` JSON Schemas |
| GET | `/api/agent-executions/` | Paginated execution history (newest first, 25/page) |
| POST | `/api/agent-executions/` | Start a new execution |
| GET | `/api/agent-executions/{id}/` | Fetch a single execution (used for polling) |

**POST**: `input` is validated by instantiating `ExecutionInputType` at the DRF serializer level — the record is never created if validation fails (400). Unknown `execution_type` also returns 400.

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

**`CatalogEnrichmentExecutionInput`** (`ExecutionInputType` subclass): fields `dataset_id: int`, `max_failures: int` (default 5).

**`CatalogEnrichmentExecution`** (`BaseAgentExecution`):
- `EXECUTION_KEY = "catalog-enrichment"`
- `run()` — iterates over all products in the dataset, drives `CatalogEnrichmentAgent` for each (full LLM loop, no user interaction), uses `ProductUpsertTracker` to stop early on too many failures, returns `ExecutionResult` with per-product outcomes

**`ProductUpsertTracker`** (`BaseExecutionValidator`): `should_continue()` returns `False` once failures reach `max_failures`; `get_issue_summary()` returns per-product failure descriptions.

---

## 6. Frontend

Three routes added to the authenticated router in `frontend/src/main.tsx`:

| Path | Component | Purpose |
|------|-----------|---------|
| `/agent-executions` | `AgentExecutionsPage` | History table + "New execution" button |
| `/agent-executions/new` | `NewAgentExecutionPage` | Select type, fill input form, submit |
| `/agent-executions/:id` | `AgentExecutionDetailPage` | Status polling + result/failure display |

API client (`frontend/src/lib/api/agent-executions.ts`) exposes `getTypes()`, `list()`, `get(id)`, `start(payload)` and is integrated into `ApiClient` via `agentExecutions()`.

`NewAgentExecutionPage` renders a dynamic form from the `execution_input_schema` JSON Schema (React Hook Form + Zod). `AgentExecutionDetailPage` polls every 3 seconds while `pending` or `in_progress`.

---

## 7. Testing

**`test_registry.py`**: `get_all()`, `get_by_key()` happy path, `get_by_key()` raises `KeyError` for unknown key.

**`test_task.py`**: `pending → in_progress → finished`; `pending → in_progress → failed` on exception.

**`test_views.py`**: types list (200); valid start (202); unknown type (400); invalid input (400, no record created); list (200); get (200); get missing (404).

**`test_product_upsert_tracker.py`**: `should_continue()` below/at threshold; `get_issue_summary()` format.

**`test_catalog_enrichment_execution.py`**: stops early when validator returns False; correct counts in `ExecutionResult.output`.

---

## 8. Implementation Order

1. **enthusiast-common** — core interfaces (`BaseAgentExecution`, `BaseExecutionValidator`, `ExecutionResult`, `ExecutionStatus`, `ExecutionInputType`)
2. **Server: Model + Migration**
3. **Server: Registry + Settings key**
4. **Server: Celery Task**
5. **Server: Serializers + Views + URLs**
6. **Server: Tests**
7. **Plugin: CatalogEnrichmentExecution** — implementation, registration, plugin tests
8. **Frontend: API Client**
9. **Frontend: Pages & Components**