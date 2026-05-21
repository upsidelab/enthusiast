# Design: agentcore / enthusiast Architecture Split

**Author:** Dawid Mularczyk

---

## Overview

Extract the domain-agnostic AI agent framework from Enthusiast into a standalone platform called **agentcore** (placeholder name — final name TBD). Enthusiast becomes an e-commerce vertical plugin installed on top of agentcore. Other verticals (healthcare, logistics, etc.) can be built the same way.

---

## Problem Statement

Enthusiast's AI agent infrastructure (conversation management, agent framework, LLM providers, memory, WebSocket streaming) is tightly coupled with e-commerce domain concepts (products, documents, DataSets). This prevents the agent core from being reused in other domains and makes the codebase harder to reason about as each layer grows.

---

## Goals

- Decouple AI agent infrastructure from e-commerce domain logic
- Make agentcore a general-purpose platform other verticals can build on
- Enthusiast becomes a true plugin — installable on agentcore with no modifications to core
- agentcore is useful standalone (without enthusiast) out of the box

---

## Non-Goals

- Abstracting over LangChain — it stays as a hard dependency in agentcore
- Building a plugin marketplace or auto-discovery mechanism — Django settings is sufficient
- Merging into a monorepo — two separate repos from day one

---

## Architecture

### Repository Structure

**Two separate repositories:**

1. `github.com/upsidelab/agentcore` — the platform
2. `github.com/upsidelab/enthusiast` — the e-commerce vertical plugin

---

### agentcore repo (the platform)

agentcore is a **runnable Django project**. Users clone/install it, configure settings, and install vertical plugins on top.

```
agentcore/
  server/
    manage.py
    settings.py             # base settings, INSTALLED_APPS = ['agentcore']
    settings_override.py    # env-based user config (add verticale here)
    pecl/
      urls.py
      wsgi.py / asgi.py
      celery.py
    docker-compose.yml
    agentcore/              # Django app
      models/               # Conversation, Message, Agent, AgenticExecution
      core/
        builder.py          # AgentBuilder (Django implementation)
        injector.py         # Injector (Django implementation)
        memory/             # PersistentChatHistory, memory strategies
        registries/         # LanguageModelRegistry, EmbeddingRegistry, etc.
        repositories.py     # Django ORM implementations of base repos
        retrievers/         # DocumentRetriever, base vector search
        callbacks/          # WebSocket callback handler
      consumers/            # Django Channels WebSocket consumer
      conversation/         # ConversationManager
      agentic_execution/    # AgenticExecution Django models, views, tasks
      views.py
      urls.py
      serializers/
      tasks.py
      admin.py
  frontend/                 # React 18 + TypeScript chat UI
  plugins/
    agentcore-common/       # Pure Python interfaces (PyPI: agentcore-common)
      agents/               # BaseAgent, BaseAgentBuilder, ConfigType
      tools/                # BaseTool, BaseFunctionTool, BaseLLMTool,
                            # BaseFileTool, BaseAgentTool
      agentic_execution/    # BaseAgenticExecutionDefinition, ExecutionResult,
                            # ToolScratchpad, BaseExecutionValidator
      registries/           # LanguageModelProvider, BaseLanguageModelRegistry,
                            # EmbeddingProvider, BaseEmbeddingProviderRegistry
      repositories/         # BaseRepository[T], BaseUserRepository,
                            # BaseConversationRepository, BaseMessageRepository,
                            # BaseDataSetRepository, BaseAgentRepository
      injectors/            # BaseInjector
      retrievers/           # BaseVectorStoreRetriever[T]
      structures/           # TextContent, LLMFile, BaseContent
      callbacks/            # ConversationCallbackHandler
      config/               # AgentConfig, LLMConfig, tool configs
      errors/               # BaseAgentFriendlyError
    agentcore-model-openai/
    agentcore-model-anthropic/
    agentcore-model-google/
    agentcore-model-mistral/
    agentcore-model-ollama/
    agentcore-model-azureopenai/
```

**What agentcore provides out of the box:**
- Conversation management (create, respond, history)
- Agent registration and execution
- WebSocket streaming of agent responses
- Agentic execution engine (autonomous multi-step tasks with retries/validators)
- LLM provider plugins (OpenAI, Anthropic, Google, Mistral, Ollama, Azure)
- Memory strategies (persistent, limited, summary)
- React chat UI
- REST API + Django admin

---

### enthusiast repo (e-commerce vertical)

enthusiast is a **Django app package** installed into agentcore. It has no `manage.py` — agentcore is the project that runs it.

```
enthusiast/
  plugins/
    enthusiast-common/      # Thin e-commerce interfaces (PyPI: enthusiast-common)
                            # NO dependency on agentcore-common
      structures/           # ProductDetails, DocumentDetails, Address,
                            # DocumentChunkDetails, ProductUpdateDetails
      interfaces/           # ProductSourcePlugin, DocumentSourcePlugin,
                            # ECommerceIntegrationPlugin
      connectors/           # ECommercePlatformConnector (ABC)
      retrievers/           # BaseProductRetriever
    enthusiast/             # Django app (PyPI: enthusiast)
      models/               # DataSet, Product, ProductChunk,
                            # Document, DocumentChunk
      catalog/              # Catalog management views/API
      sync/                 # Source synchronization engine
      injector.py           # EnthusiastInjector (extends BaseInjector)
      builder.py            # EnthusiastAgentBuilder (extends BaseAgentBuilder)
      repositories.py       # Django ORM implementations for e-commerce models
      retrievers/           # ProductRetriever, DocumentRetriever (pgvector)
      admin.py
      urls.py
      serializers/
    enthusiast-agent-product-search/
    enthusiast-agent-catalog-enrichment/
    enthusiast-agent-order-intake/
    enthusiast-agent-user-manual-search/
    enthusiast-agent-invoice-scanning/
    enthusiast-source-medusa/
    enthusiast-source-shopify/
    enthusiast-source-woocommerce/
    enthusiast-source-shopware/
    enthusiast-source-solidus/
    enthusiast-source-wordpress/
    enthusiast-source-sanitycms/
    enthusiast-source-sample/
```

---

### Package Dependency Graph

```
agentcore-common          (langchain, pydantic — no project deps)
      ↑                              ↑
agentcore (Django app)         agentcore-model-*


enthusiast-common         (no dependency on agentcore-common — fully independent)
      ↑                              ↑               ↑
enthusiast (Django app)    enthusiast-agent-*    enthusiast-source-*
      ↑                         ↑
   agentcore              agentcore-common
                          enthusiast-common
```

Key rule: **`enthusiast-common` has zero dependency on `agentcore-common`**. E-commerce interfaces are fully independent of the AI agent framework.

---

### Plugin Registration (Django settings)

agentcore `settings.py` defines base config. Users extend via `settings_override.py`:

```python
# agentcore/server/settings.py
INSTALLED_APPS = [
    'agentcore',
    # vertical plugins added via settings_override:
]

AGENTCORE_LANGUAGE_MODEL_PLUGINS = [
    'agentcore_model_openai.OpenAILanguageModelProvider',
    'agentcore_model_anthropic.AnthropicLanguageModelProvider',
    'agentcore_model_google.GoogleLanguageModelProvider',
    'agentcore_model_mistral.MistralLanguageModelProvider',
    'agentcore_model_ollama.OllamaLanguageModelProvider',
    'agentcore_model_azureopenai.AzureOpenAILanguageModelProvider',
]
AGENTCORE_AGENT_PLUGINS = []
AGENTCORE_EMBEDDING_PLUGINS = []

# agentcore/server/settings_override.py (user-configured, env-based)
INSTALLED_APPS += ['enthusiast']

AGENTCORE_AGENT_PLUGINS = [
    'enthusiast_agent_product_search.ProductSearchAgent',
    'enthusiast_agent_catalog_enrichment.CatalogEnrichmentAgent',
    'enthusiast_agent_order_intake.OrderIntakeAgent',
    'enthusiast_agent_user_manual_search.UserManualSearchAgent',
    'enthusiast_agent_invoice_scanning.InvoiceScanningAgent',
]
AGENTCORE_SOURCE_PLUGINS = [
    'enthusiast_source_medusa.MedusaIntegration',
    # ...
]
```

Each vertical plugin follows the same pattern — never modifies agentcore settings directly.

---

### How enthusiast extends agentcore

enthusiast provides Django-specific implementations of agentcore's abstract bases:

```python
# enthusiast/injector.py
from agentcore_common.injectors import BaseInjector
from enthusiast_common.retrievers import BaseProductRetriever

class EnthusiastInjector(BaseInjector):
    def __init__(self, ..., product_retriever: BaseProductRetriever):
        super().__init__(...)
        self._product_retriever = product_retriever

    @property
    def product_retriever(self) -> BaseProductRetriever:
        return self._product_retriever

# enthusiast/builder.py
from agentcore.core.builder import AgentBuilder  # Django agentcore builder

class EnthusiastAgentBuilder(AgentBuilder):
    def _build_injector(self) -> EnthusiastInjector:
        # builds product retriever, passes to EnthusiastInjector
        ...
```

---

## What Moves Where

### From enthusiast → agentcore
| Current location | New location |
|---|---|
| `plugins/enthusiast-common/` (generic parts) | `plugins/agentcore-common/` |
| `plugins/enthusiast-model-*` | `plugins/agentcore-model-*` |
| `server/agent/core/` | `server/agentcore/core/` |
| `server/agent/` (Conversation, Message, Agent models) | `server/agentcore/models/` |
| `server/agent/conversation/` | `server/agentcore/conversation/` |
| `server/agent/agentic_execution/` (Django layer) | `server/agentcore/agentic_execution/` |
| `server/agent/consumers/` | `server/agentcore/consumers/` |
| `server/account/` | `server/account/` (stays, generic auth) |
| `frontend/` | `agentcore/frontend/` |
| `server/pecl/` (project config) | `agentcore/server/pecl/` |

### Stays in enthusiast
| Current location | Notes |
|---|---|
| `plugins/enthusiast-common/` (e-commerce parts) | Becomes thin `enthusiast-common` |
| `plugins/enthusiast-agent-*` | All e-commerce agents |
| `plugins/enthusiast-source-*` | All source plugins |
| `server/catalog/` | Moves into `plugins/enthusiast/catalog/` |
| `server/sync/` | Moves into `plugins/enthusiast/sync/` |

### Renamed
| Old name | New name |
|---|---|
| `enthusiast-model-openai` | `agentcore-model-openai` |
| `enthusiast-model-anthropic` | `agentcore-model-anthropic` |
| `enthusiast-model-google` | `agentcore-model-google` |
| `enthusiast-model-mistral` | `agentcore-model-mistral` |
| `enthusiast-model-ollama` | `agentcore-model-ollama` |
| `enthusiast-model-azureopenai` | `agentcore-model-azureopenai` |
| `enthusiast_common.*` (generic imports) | `agentcore_common.*` |

---

## Migration Strategy

### Phase 1 — Build agentcore (green field, new repo)

1. Create `github.com/upsidelab/agentcore`
2. Copy and refactor:
   - `enthusiast-common` → `agentcore-common` (strip all e-commerce types)
   - `enthusiast-model-*` → `agentcore-model-*` (rename packages + imports)
   - `server/agent/` → `agentcore/server/agentcore/` (Django app)
   - `server/account/` → agentcore (generic auth)
   - `server/pecl/` → agentcore project config
   - `frontend/` → agentcore frontend
3. agentcore runs standalone, all existing tests pass
4. Publish `agentcore-common` and `agentcore` to PyPI (alpha)

### Phase 2 — Migrate enthusiast (branch on enthusiast repo)

1. Create branch `feature/agentcore-migration` on enthusiast
2. Remove from enthusiast:
   - `enthusiast-common` generic parts
   - All `enthusiast-model-*` packages
   - `server/agent/core/` (builder, injector, registries, memory)
   - `server/agent/` (Conversation, Message, Agent Django models)
   - `server/account/`
   - `frontend/`
3. Thin `enthusiast-common`: keep only e-commerce interfaces
4. Update all imports: `enthusiast_common.*` → `agentcore_common.*`
5. Add `agentcore` as dependency in `pyproject.toml`
6. Implement `EnthusiastInjector`, `EnthusiastAgentBuilder` extending agentcore bases
7. End-to-end tests: agentcore + enthusiast plugin working together
8. Merge branch

### Phase 3 — Release

1. Publish `enthusiast-common` and `enthusiast` to PyPI
2. `docker-compose.yml` in agentcore repo with enthusiast pre-installed as reference setup
3. Update documentation

---

## Workspace Model (resolved)

The `Conversation → DataSet` circular dependency is resolved by introducing a generic `Workspace` model in agentcore. All verticale extend it via `OneToOne`.

```python
# agentcore
class Workspace(models.Model):
    name = CharField()
    owner = FK(User)
    created_at = DateTimeField()
    llm_provider = CharField()     # platform-level LLM config
    llm_model = CharField()

class Agent(models.Model):
    workspace = FK(Workspace)

class Conversation(models.Model):
    workspace = FK(Workspace)

# enthusiast
class DataSet(models.Model):
    workspace = OneToOneField(Workspace, related_name='dataset')
    language = CharField()
    embedding_provider = CharField()   # tied to pgvector store
    embedding_model = CharField()
    # source integration configs
```

**Config override cascade:**
```
[1] settings.py defaults      (DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL)
[2] Workspace                 (llm_provider, llm_model) — agentcore
[3] DataSet                   (embedding_provider, embedding_model) — enthusiast
[4] Agent config              (system_prompt, tools, memory) — agentcore
```

`AgentBuilder` (agentcore) handles levels 1–2. `EnthusiastAgentBuilder` handles level 3.

## Frontend Architecture Discussion

The frontend work is split into two iterations with a clear decision point between them.

---

### Iteration 1 — Django staticfiles bundle (decided, implement now)

The plugin extension mechanism is intentionally simple for the first iteration. No NPM infrastructure, no package publishing, no shared types. The goal is to get the plugin system working end-to-end.

**How it works:**

```
enthusiast/static/enthusiast/frontend/bundle.js  ← pre-built, ships with pip package
AppConfig.ready() → register_frontend_plugin(id, bundle_url)
GET /api/config/ → { plugins: [{ bundle: "/static/enthusiast/frontend/bundle.js" }] }
shell → <script src="bundle.js"> → window.agentcore.registerPlugin({nav, routes})
```

**Plugin registration (global contract via `window.agentcore`):**

```typescript
// enthusiast bundle.js — called on load, no imports from agentcore
window.agentcore.registerPlugin({
  id: 'enthusiast',
  nav: [
    { label: 'Catalog',      path: '/catalog' },
    { label: 'Integrations', path: '/integrations' },
  ],
  routes: [
    { path: '/catalog/*',      componentId: 'CatalogApp' },
    { path: '/integrations/*', componentId: 'IntegrationsApp' },
  ],
  toolRenderers: {
    'product_search': 'ProductSearchRenderer',
    'order_intake':   'OrderIntakeRenderer',
  },
})
```

**What ships in Iteration 1:**
- agentcore frontend: existing React shell with a `pluginRegistry` module, `window.agentcore.registerPlugin()` global, dynamic `<script>` injection from `/api/config/`
- enthusiast frontend: existing React app compiled to `bundle.js`, copied to `enthusiast/static/`, committed to git, shipped with pip package

**Known limitations (acceptable for now):**
- No TypeScript types shared between shell and plugins — plugin developers need to know the `registerPlugin()` contract by reading docs
- Plugin components can't import from agentcore's component library — no shared UI primitives
- DX friction: to develop the enthusiast frontend you need a running agentcore instance

These limitations are intentional trade-offs to unblock the backend architecture work (Plans 1–3) and ship a working plugin system quickly.

---

### Iteration 2 — Frontend architecture (deferred, consult with Filip)

Once Plans 1–3 are shipped and the backend plugin system is stable, the frontend injection approach from Iteration 1 will have served its purpose but will show its limits — no shared types, no shared component library, DX friction when developing plugin frontend without a running agentcore.

**Before starting Iteration 2, schedule a meeting with Filip (frontend developer).** The whole frontend strategy should be his call — he will know what's practical. Topics to bring:

- **Overall strategy** — is the staticfiles bundle + injection approach worth keeping long-term, or should we replace it with something fundamentally different?
- **Chat UI library** — current chat UI is custom-built. Is there a library worth adopting (e.g. assistant-ui, or something else Filip would recommend)?
- **Shared frontend packages** — does it make sense to extract shared types/components into packages (`@agentcore/ui`, `@enthusiast/ui`)? Or is it over-engineering for the team size?
- **Separate frontend repo** — should the frontend live in its own repo, separate from the Python repos? Filip may prefer that as a frontend developer.
- **Build pipeline** — how does the enthusiast bundle get built and shipped with the pip package in a maintainable way?

No decisions are made here — this is a conversation to have with Filip, not a spec to lock in upfront.

---

## Open Questions

- **Final name for agentcore** — placeholder only, needs branding discussion
- **PyPI namespace** — check `agentcore` availability before publishing
- **Versioning strategy** — agentcore and enthusiast version independently
- **Workspace → DataSet extension pattern** — current decision is `DataSet OneToOne Workspace`, but this needs more thought. Is OneToOne the right Django pattern here? Could it create awkward joins or leaky abstractions when multiple verticale are installed? Are there better patterns (e.g. multi-table inheritance, a pure FK from DataSet with no back-reference on Workspace)? To be revisited before implementation of the data model.
- **Frontend architecture (Iteration 2)** — Iteration 1 decided: Django staticfiles bundle + `window.agentcore.registerPlugin()`. Iteration 2 fully open: needs a meeting with Filip (frontend developer) to decide on chat UI library, shared package strategy, separate frontend repo, and build pipeline. See Frontend Architecture Discussion for details.

---

## Plugin Developer Documentation (needed before public release)

Before agentcore can be used by third parties, we need a "Build your own vertical" guide. enthusiast is the reference implementation, but someone building a healthcare or logistics plugin shouldn't need to read its source code to understand what to implement.

The guide should cover:

### What agentcore exposes (the extension points)

**Must implement** — these are abstract, agentcore won't run without a concrete implementation:

| Class | Where | What to implement |
|---|---|---|
| `BaseInjector` | `agentcore-common` | `document_retriever`, `chat_history`, `tool_scratchpad` properties |
| `BaseAgentBuilder` | `agentcore-common` | `_build_injector()`, `_build_llm_registry()`, `_build_tools()`, `_build_agent()`, and related factory methods |
| `BaseConversationRepository` | `agentcore-common` | `get_workspace_id()`, `get_agent_id()`, `list_files()`, `get_file_objects()` |
| `BaseWorkspaceRepository` | `agentcore-common` | standard CRUD methods from `BaseRepository` |

**Can implement** — optional extension points that unlock additional capabilities:

| Class | What it adds |
|---|---|
| `BaseAgent` subclass | Custom agent with domain-specific `get_answer()` logic |
| `BaseFunctionTool` | A simple tool the agent can call (e.g. `lookup_patient_record`) |
| `BaseLLMTool` | A tool that itself calls an LLM (e.g. summariser, classifier) |
| `BaseAgentTool` | A tool that spawns a sub-agent |
| `BaseAgenticExecutionDefinition` | An autonomous multi-step task with retry/validation loop |
| `LanguageModelProvider` | A new LLM provider (if not covered by agentcore-model-*) |

**Django integration** — what the plugin's Django app must/can provide:

| Item | Required? | Purpose |
|---|---|---|
| `AppConfig.ready()` calls `register_frontend_plugin()` | optional | registers frontend bundle with agentcore shell |
| `INSTALLED_APPS` entry | required | Django discovers models, migrations, admin |
| `settings_override.py` entries (`AGENTCORE_AGENT_PLUGINS`, etc.) | required | registers agents, sources with agentcore registries |
| `OneToOneField(Workspace, related_name='+')` on domain model | recommended | extends Workspace with vertical-specific config |

### What the guide should walk through step by step

1. Create a new Python package (pip-installable)
2. Define a domain model extending `Workspace` via `OneToOneField`
3. Implement `BaseInjector` with domain-specific retrievers
4. Implement `BaseAgentBuilder` wiring up the injector and tools
5. Write a simple `BaseFunctionTool`
6. Register everything in `settings_override.py`
7. Write a minimal frontend bundle that calls `window.agentcore.registerPlugin()`
8. Ship it: `pip install yourplugin` + `INSTALLED_APPS += ['yourplugin']`

enthusiast itself serves as the living reference for all of the above.

---

## Success Criteria

- agentcore runs standalone with a working chat UI and conversation API, zero e-commerce imports
- enthusiast installs into agentcore via `INSTALLED_APPS` and `pip install enthusiast`
- A hypothetical healthcare plugin could follow the same pattern as enthusiast
- All existing enthusiast tests pass after migration
- No circular dependencies between packages
