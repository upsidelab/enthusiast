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
    agentcore_project/      # Django project config (replaces old 'pecl' name)
      urls.py
      wsgi.py / asgi.py
      celery.py
    docker-compose.yml
    agentcore/              # Django app
      models/               # DataSet, Integration,
                            # Conversation, Message, Agent, AgenticExecution
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
- Agent registration and execution (global registry, `AppConfig.ready()` pattern)
- `ToolCallingAgent` — generic tool-calling agent, no built-in tools (plugins register tools)
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
      models/               # Product, ProductChunk, Document, DocumentChunk
                            # all with FK to agentcore.DataSet
      apps.py               # AppConfig.ready() registers builder, tools, integrations
      sync/                 # Source synchronization engine (products + documents)
      integrations/         # MedusaIntegration, ShopifyIntegration handlers
      injector.py           # EnthusiastInjector — implements get_retriever(type)
      builder.py            # EnthusiastAgentBuilder (extends BaseAgentBuilder)
      repositories.py       # Django ORM implementations for e-commerce models
      retrievers/           # ProductRetriever, DocumentRetriever (pgvector)
      tools/                # ProductSearchTool, DocumentSearchTool, OrderManagementTool
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
    # vertical plugins added via settings_override
]

AGENTCORE_LANGUAGE_MODEL_PLUGINS = [
    'agentcore_model_openai.OpenAILanguageModelProvider',
    'agentcore_model_anthropic.AnthropicLanguageModelProvider',
    'agentcore_model_google.GoogleLanguageModelProvider',
    'agentcore_model_mistral.MistralLanguageModelProvider',
    'agentcore_model_ollama.OllamaLanguageModelProvider',
    'agentcore_model_azureopenai.AzureOpenAILanguageModelProvider',
]
AGENTCORE_EMBEDDING_PLUGINS = []
AGENTCORE_AGENT_PLUGINS = []
AGENTCORE_TOOL_PLUGINS = []
AGENTCORE_BUILDER_PLUGINS = []
AGENTCORE_INTEGRATION_PLUGINS = []

# agentcore/server/settings_override.py (user-configured, env-based)
INSTALLED_APPS += ['enthusiast']

AGENTCORE_AGENT_PLUGINS = [
    'enthusiast_agent_product_search.ProductSearchAgent',
    'enthusiast_agent_catalog_enrichment.CatalogEnrichmentAgent',
    'enthusiast_agent_order_intake.OrderIntakeAgent',
    'enthusiast_agent_user_manual_search.UserManualSearchAgent',
    'enthusiast_agent_invoice_scanning.InvoiceScanningAgent',
]
AGENTCORE_TOOL_PLUGINS = [
    'enthusiast.tools.ProductSearchTool',
    'enthusiast.tools.DocumentSearchTool',
    'enthusiast.tools.OrderManagementTool',
]
AGENTCORE_BUILDER_PLUGINS = [
    'enthusiast.builder.EnthusiastAgentBuilder',
]
AGENTCORE_INTEGRATION_PLUGINS = [
    'enthusiast.integrations.MedusaIntegration',
    'enthusiast.integrations.ShopifyIntegration',
]
```

Each vertical plugin follows the same pattern — never modifies agentcore settings directly.

---

### How enthusiast extends agentcore

enthusiast is registered entirely through `settings_override.py`. agentcore reads the settings lists at startup and loads the declared classes — no runtime `register()` calls, no `AppConfig.ready()` magic.

```python
# enthusiast/injector.py
from agentcore_common.injectors import BaseInjector

class EnthusiastInjector(BaseInjector):
    def get_retriever(self, repository_type: str):
        if repository_type == 'products':
            return self._product_retriever
        elif repository_type == 'documents':
            return self._document_retriever
        raise ValueError(f"No retriever for repository type: {repository_type}")

# enthusiast/builder.py
from agentcore_common.agents import BaseAgentBuilder

class EnthusiastAgentBuilder(BaseAgentBuilder):
    def _build_injector(self) -> EnthusiastInjector:
        # reads dataset.embedding_provider, dataset.embedding_model from DataSet
        # builds product + document retrievers, passes to EnthusiastInjector
        ...

    def _build_tools(self) -> list[BaseTool]:
        # instantiates tools from AGENTCORE_TOOL_PLUGINS
        ...
```

**Repositories are code-defined, not UI-created.** When enthusiast is installed, every DataSet automatically has product and document retrieval capabilities — no "Add Repository" step in UI. The admin sees this reflected in "Agent Capabilities", not in a repository list.

Enthusiast's models (`Product`, `Document`, `ProductChunk`, `DocumentChunk`) all have a direct FK to `DataSet` from agentcore. No OneToOne extension of DataSet is needed — all configuration lives in `DataSet` itself (LLM config, embedding config) or in enthusiast's own `Integration` records.

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

### New in agentcore (greenfield)
| What | Notes |
|---|---|
| `agentcore/models/dataset.py` | `DataSet` model — replaces `Workspace`, holds LLM + embedding config |
| `agentcore/models/integration.py` | `Integration` model — generic external system connector, type defined by plugin |
| `agentcore/registry/` | Loads plugin classes from settings lists at startup (`AGENTCORE_*_PLUGINS`) |
| `agentcore/agents/tool_calling.py` | `ToolCallingAgent` — generic tool-calling agent, no built-in tools |

### Stays in enthusiast
| Current location | Notes |
|---|---|
| `plugins/enthusiast-common/` (e-commerce parts) | Becomes thin `enthusiast-common` |
| `plugins/enthusiast-agent-*` | All e-commerce agents |
| `plugins/enthusiast-source-*` | All source plugins |
| `server/catalog/` | Moves into `plugins/enthusiast/` (sync engine only, no DataSet) |
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

## Data Model (resolved)

`DataSet` replaces `Workspace` as the central tenant model and moves to agentcore. It is fully generic — no e-commerce concepts. Plugins do **not** extend DataSet via OneToOne — all shared configuration (LLM + embedding) lives directly on `DataSet`. Plugin models (e.g. `Product`, `Document`) reference `DataSet` via a plain FK.

There is no `Repository` model in agentcore. Repositories are code-defined by plugins — installed automatically when a plugin is added to `INSTALLED_APPS`, not created through the UI.

```python
# agentcore — all generic, no e-commerce concepts

class DataSet(models.Model):
    name = CharField()
    owner = FK(User)
    created_at = DateTimeField()
    # LLM config — selected per DataSet in UI, credentials in env vars
    llm_provider = CharField()
    llm_model = CharField()
    # Embedding config — agentcore stores these, plugins read and use them
    embedding_provider = CharField()
    embedding_model = CharField()
    embedding_dimensions = IntegerField()
    chunk_size = IntegerField()
    chunk_overlap = IntegerField()

class Integration(models.Model):
    """External system connection (e.g. Medusa, Shopify). Type and config defined by plugin."""
    dataset = FK(DataSet)
    name = CharField()
    type = CharField()       # e.g. 'medusa', 'shopify' — registered by plugin
    config = JSONField()     # URLs, non-sensitive config — schema defined by plugin

class Agent(models.Model):
    dataset = FK(DataSet)

class Conversation(models.Model):
    dataset = FK(DataSet)
```

**Sensitive credentials** (API keys, tokens) always go to environment variables — never stored in `Integration.config`.

```python
# enthusiast — e-commerce models reference DataSet directly
class Product(models.Model):
    dataset = FK("agentcore.DataSet")
    ...

class Document(models.Model):
    dataset = FK("agentcore.DataSet")
    ...
```

agentcore has **no knowledge** of what `type` means for Integration — it is a black box. The plugin registers a handler in `AppConfig.ready()` and agentcore renders a generic config form using the JSON Schema the plugin provides.

**BaseInjector (agentcore-common) — generic retriever access:**
```python
class BaseInjector(ABC):
    @abstractmethod
    def get_retriever(self, repository_type: str) -> BaseVectorStoreRetriever:
        pass

    @property
    @abstractmethod
    def chat_history(self) -> BaseChatMessageHistory:
        pass

    @property
    @abstractmethod
    def tool_scratchpad(self) -> ToolScratchpad:
        pass
```

No hardcoded `product_retriever` or `document_retriever` — those are enthusiast concerns.

**EnthusiastInjector (enthusiast) — implements retriever lookup by type:**
```python
class EnthusiastInjector(BaseInjector):
    def get_retriever(self, repository_type: str) -> BaseVectorStoreRetriever:
        if repository_type == 'products':
            return self._product_retriever
        elif repository_type == 'documents':
            return self._document_retriever
        raise ValueError(f"No retriever for repository type: {repository_type}")
```

**enthusiast tools use the generic interface:**
```python
class ProductSearchTool(BaseFunctionTool):
    def run(self, query: str):
        retriever = self._injector.get_retriever('products')
        return retriever.search(query)
```

**Config cascade:**
```
[1] settings.py / env vars    sensitive credentials only (OPENAI_API_KEY etc.)
[2] DataSet                   llm_provider, llm_model,
                              embedding_provider, embedding_model,
                              embedding_dimensions, chunk_size, chunk_overlap
[3] Agent config              system_prompt, tools, memory strategy
```

Embedding config lives on `DataSet`, not per-repository. All DataSet config is set in the UI at creation time — no settings file entries for these values.

## Frontend Architecture

agentcore's frontend provides a **complete, working UI without any plugin injection**.

**agentcore frontend covers:**
```
Conversations     ← chat, history, WebSocket streaming
DataSets          ← list, create, configure (LLM + embedding)
  └── Integrations  ← add/configure external systems (generic — type + config form)
Agent Capabilities  ← auto-discovered from registry (read-only, code-defined)
Settings          ← LLM providers, embedding providers
```

**Repositories are not managed in the UI.** When enthusiast is installed, product and document retrieval capabilities appear automatically in "Agent Capabilities" — the admin does not create or configure them. Only `Integration` records (e.g. Medusa API connection) require UI configuration.

**enthusiast is pure backend.** No `bundle.js`, no `window.agentcore.registerPlugin()`, no staticfiles frontend. The plugin injection system is not needed.

---

### Custom frontend (deferred, consult with Filip)

If a team wants a richer UI beyond what agentcore's generic views provide — e.g. a full product catalog grid with images and filters, or custom tool output renderers that show `<ProductCard>` instead of JSON in the chat — that's a separate decision.

**Before building any custom frontend, schedule a meeting with Filip (frontend developer).** Topics:
- Is agentcore's generic UI sufficient for the e-commerce use case, or do we need a custom Catalog page?
- Chat UI library — is there something worth adopting (e.g. assistant-ui)?
- If custom frontend is needed: separate repo, NPM packages, or something else?
- Tool output renderers — do we need them, and how should they work?

No decisions locked in here.

---

## Open Questions

- **Final name for agentcore** — placeholder only, needs branding discussion
- **PyPI namespace** — check `agentcore` availability before publishing
- **Versioning strategy** — agentcore and enthusiast version independently
- **Integration config schema** — how does agentcore know what fields to show when configuring a plugin-defined Integration type? Recommendation: plugin registers a JSON Schema in `AppConfig.ready()`, agentcore renders a generic form (e.g. via `react-jsonschema-form`). Same pattern as Airbyte connector config. Needs confirmation before building the Integration configuration UI.
- **Custom frontend** — agentcore's generic UI covers DataSet/Integration management and a read-only Agent Capabilities view. Whether enthusiast needs a richer Catalog page (products grid, document browser) or custom chat tool renderers is deferred. Consult with Filip before any frontend work begins.

---

## Plugin Developer Documentation (needed before public release)

Before agentcore can be used by third parties, we need a "Build your own vertical" guide. enthusiast is the reference implementation, but someone building a healthcare or logistics plugin shouldn't need to read its source code to understand what to implement.

The guide should cover:

### What agentcore exposes (the extension points)

**Must implement** — these are abstract, agentcore won't run without a concrete implementation:

| Class | Where | What to implement |
|---|---|---|
| `BaseInjector` | `agentcore-common` | `get_retriever(type)`, `chat_history`, `tool_scratchpad` |
| `BaseAgentBuilder` | `agentcore-common` | `_build_injector()`, `_build_llm_registry()`, `_build_tools()`, `_build_agent()`, and related factory methods |
| `BaseConversationRepository` | `agentcore-common` | `get_dataset_id()`, `get_agent_id()`, `list_files()`, `get_file_objects()` |
| `BaseDataSetRepository` | `agentcore-common` | standard CRUD methods from `BaseRepository` |

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
| `INSTALLED_APPS` entry | required | Django discovers models, migrations, admin |
| `AGENTCORE_BUILDER_PLUGINS` entry | required | agentcore loads your AgentBuilder |
| `AGENTCORE_TOOL_PLUGINS` entries | required | agentcore loads your tools |
| `AGENTCORE_AGENT_PLUGINS` entries | required | agentcore exposes your agents in the UI |
| `AGENTCORE_INTEGRATION_PLUGINS` entries | optional | registers integration types with config schema |

### What the guide should walk through step by step

1. Create a new Python package (pip-installable)
2. Define your domain models with FK to `agentcore.DataSet`
3. Implement `BaseInjector.get_retriever(type)` for your data types
4. Implement `BaseAgentBuilder` — wires up injector, reads DataSet embedding config, builds tools
5. Write domain-specific tools using `self._injector.get_retriever('your_type')`
6. Add entries to `settings_override.py`: `AGENTCORE_BUILDER_PLUGINS`, `AGENTCORE_TOOL_PLUGINS`, `AGENTCORE_AGENT_PLUGINS`
7. Ship it: `pip install yourplugin` + add settings entries

enthusiast itself serves as the living reference for all of the above.

---

## Success Criteria

- agentcore runs standalone with a working chat UI and conversation API, zero e-commerce imports
- enthusiast installs into agentcore via `INSTALLED_APPS` and `pip install enthusiast`
- A hypothetical healthcare plugin could follow the same pattern as enthusiast
- All existing enthusiast tests pass after migration
- No circular dependencies between packages
