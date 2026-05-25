# Design: agentcore / enthusiast Architecture Split

**Author:** Dawid Mularczyk

---

## Problem

Enthusiast's AI agent infrastructure is tightly coupled with e-commerce domain concepts (products, documents, catalog). This prevents the agent framework from being reused in other domains and makes the codebase harder to reason about as each layer grows.

---

## Goal

Extract a standalone AI agent platform (**agentcore** — name TBD) that is completely domain-agnostic. Enthusiast becomes an e-commerce vertical plugin that installs on top of agentcore. Other verticals (healthcare, logistics, etc.) can be built the same way.

---

## Two Repositories

**`agentcore`** — the platform. A runnable Django project. Users clone it, configure settings, and install vertical plugins on top.

**`enthusiast`** — the e-commerce vertical. A Django app package installed into agentcore via `INSTALLED_APPS`. Has no `manage.py` of its own.

---

## agentcore as the Building Block

agentcore is a pure AI agent framework — it knows nothing about products, documents, patients, or any other domain. It provides the infrastructure that all verticals share:

- **DataSet** — central tenant concept. Holds LLM config, embedding config. All plugin models anchor to it via FK. Replaces the current Workspace.
- **Conversation / Message / Agent** — core conversation management
- **AgenticExecution** — autonomous multi-step task execution with retries
- **ToolCallingAgent** — generic tool-calling agent. No built-in tools — plugins bring their own.
- **Integration** — one external system connection per DataSet (type and config defined by the plugin, configured in the UI)
- **LLM provider plugins** — OpenAI, Anthropic, Google, Mistral, Ollama, Azure
- **WebSocket streaming, memory strategies, REST API**

A vertical plugin fills in everything domain-specific: what data to index, how to search it, what tools to expose to the agent.

```
┌──────────────────────────────────────────┐
│                agentcore                 │
│                                          │
│  DataSet         ◄── FK (from plugin) ◄──┼──┐
│  Conversation                            │  │
│  Agent                                   │  │
│  AgenticExecution                        │  │
│  ToolCallingAgent                        │  │
│  Integration (1 per type per DataSet)    │  │
│                                          │  │
│  settings_override.py:                   │  │
│    AVAILABLE_AGENTS            ──────────┼──┼──► loads classes
│    AGENTCORE_TOOL_PLUGINS      ──────────┼──┼──► loads classes
│    AGENTCORE_BUILDER_PLUGINS   ──────────┼──┼──► loads classes
│    AGENTCORE_INTEGRATION_PLUGINS ────────┼──┼──► loads classes
└──────────────────────────────────────────┘  │
                    ▲                          │
                    │  INSTALLED_APPS +=       │
                    │  ['enthusiast']          │
                    │  + settings lists        │
                    │                          │
┌──────────────────────────────────────────┐  │
│               enthusiast                 │  │
│                                          │  │
│  Product  ──────────────────── FK ───────┼──┘
│  Document ──────────────────── FK ───────┼──┘
│                                          │
│  EnthusiastAgentBuilder                  │
│    builds: injector + tools              │
│                                          │
│  ProductSearchTool                       │
│  DocumentSearchTool                      │
│  OrderManagementTool                     │
│                                          │
│  MedusaIntegration                       │
│  enthusiast-source-medusa (sync)         │
└──────────────────────────────────────────┘
```

```
User message
    │
    ▼
ConversationManager (agentcore)
    │  reads AGENTCORE_BUILDER_PLUGINS from settings
    │  loads EnthusiastAgentBuilder
    ▼
EnthusiastAgentBuilder (enthusiast)
    │  reads dataset.embedding_model
    │  builds ProductRetriever, DocumentRetriever
    │  returns ToolCallingAgent with tools
    ▼
ToolCallingAgent (agentcore)
    │  LangChain tool-calling loop
    │  calls ProductSearchTool.run(query)
    ▼
ProductSearchTool (enthusiast)
    │  vector search on ProductChunk via pgvector
    │  returns results
    ▼
LLM generates response → WebSocket → User
```

---

## How a Vertical Plugin Works

A plugin is responsible for three things:

**1. Repositories — the domain knowledge**

The plugin defines what data sources exist and how to search them. These are not models in agentcore — they are defined entirely by the plugin. Examples:

| Vertical | Repositories |
|---|---|
| enthusiast (e-commerce) | Products, Documents |
| healthcare | Patient records, Clinical notes |
| logistics | Shipments, Warehouses |

The plugin owns the models (with FK to `agentcore.DataSet`), the sync logic, the embeddings, and the vector search. agentcore is unaware of any of this.

Repositories are **code-defined** — the admin does not create them in the UI. They exist automatically when the plugin is installed. The UI shows them read-only per DataSet so the admin can see what knowledge sources are available. The exact name for this UI section is TBD (deferred to the frontend discussion).

**2. Integration — the external system**

A DataSet can have multiple integrations — one per type (e.g. Medusa + Shopify on the same DataSet). The plugin defines the Integration type:

```python
class MedusaIntegration(BaseIntegration):
    type = 'medusa'
    label = 'Medusa'

    def get_config_schema(self): ...   # drives the UI config form
    def test_connection(self, config): ...
    def get_client(self, config): ...
```

Integration config (URL, API key) is stored per-DataSet in the database — not in env vars, because each DataSet connects to a different store instance.

**3. AgentBuilder + Tools — how the agent is assembled**

The plugin provides a builder that wires up its repositories and tools into an agent that agentcore can run:

```python
class EnthusiastAgentBuilder(BaseAgentBuilder):
    def build(self, dataset, conversation):
        # reads embedding config from dataset
        # builds product + document retrievers
        # instantiates injector and tools
        # returns a ToolCallingAgent ready to answer questions
        ...
```

---

## Plugin Registration

Plugins register with agentcore via `settings_override.py`:

```python
# settings_override.py
INSTALLED_APPS += ['enthusiast']

AGENTCORE_BUILDER_PLUGINS     = ['enthusiast.builder.EnthusiastAgentBuilder']
AGENTCORE_TOOL_PLUGINS        = ['enthusiast.tools.ProductSearchTool', ...]
AGENTCORE_AGENT_PLUGINS       = ['enthusiast_agent_product_search.ProductSearchAgent', ...]
AGENTCORE_INTEGRATION_PLUGINS = ['enthusiast.integrations.MedusaIntegration', ...]
```

agentcore reads these lists at startup and loads the declared classes. One mechanism, no magic.

---

## What enthusiast Brings

enthusiast is the reference implementation of a vertical plugin:

- **Product / Document models** — with FK to `agentcore.DataSet`
- **Sync engine** — pulls data from Medusa, Shopify, etc. and stores embeddings
- **Tools** — ProductSearchTool, DocumentSearchTool, OrderManagementTool
- **AgentBuilder + Injector** — wires up e-commerce retrievers and tools
- **Source plugins** — `enthusiast-source-medusa`, `enthusiast-source-shopify`, etc.
- **Agent plugins** — ProductSearchAgent, CatalogEnrichmentAgent, OrderIntakeAgent, etc.

---

## Package Structure

```
agentcore/
  plugins/
    agentcore-common/     # Pure Python ABCs — BaseAgent, BaseAgentBuilder,
                          # BaseTool, BaseInjector, BaseVectorStoreRetriever,
                          # BaseIntegration, etc.
    agentcore-model-*/    # LLM provider plugins (renamed from enthusiast-model-*)
  server/
    agentcore/            # Django app
    frontend/             # React UI

enthusiast/
  plugins/
    enthusiast-common/    # Pure Python e-commerce structs — ProductDetails,
                          # DocumentDetails, BaseProductRetriever, etc.
                          # Zero dependency on agentcore-common.
    enthusiast/           # Django app — Product, Document, tools, builder, injector
    enthusiast-agent-*/   # Agent plugins
    enthusiast-source-*/  # Source sync plugins (Medusa, Shopify, etc.)
```

Key rule: `enthusiast-common` has **zero dependency on `agentcore-common`**. E-commerce interfaces are fully independent of the AI agent framework.

---

## Frontend

> **Note:** At this stage there is no frontend plan beyond writing it manually. agentcore ships a React UI for chat, DataSet management, and Integration configuration. Any richer plugin-specific UI (e.g. a Catalog page for products and documents) requires manual frontend development — no injection mechanism exists. This is a known gap to address in a future iteration, ideally after a consultation with a frontend developer.

---

## Migration Plan

### Phase 1 — Build agentcore (new repo, green field)
- Extract `enthusiast-common` generic parts → `agentcore-common`
- Rename `enthusiast-model-*` → `agentcore-model-*`
- Move agent infrastructure (Conversation, Agent, AgenticExecution, ConversationManager) → agentcore Django app
- Add DataSet model (replaces Workspace), Integration model
- agentcore runs standalone with a working chat UI

### Phase 2 — Migrate enthusiast (branch on enthusiast repo)
- Remove everything that moved to agentcore
- Thin `enthusiast-common` to e-commerce structs only
- Implement `EnthusiastAgentBuilder` and `EnthusiastInjector` extending agentcore-common bases
- Product / Document models reference `agentcore.DataSet` via FK
- End-to-end: agentcore + enthusiast plugin working together

### Phase 3 — Release
- Publish packages to PyPI
- Reference `docker-compose.yml` with enthusiast pre-installed
- "Build your own vertical" developer guide

---

## Open Questions

- **Final name for agentcore** — placeholder only, needs branding discussion
- **PyPI namespace** — check `agentcore` availability
- **Versioning** — agentcore and enthusiast version independently
