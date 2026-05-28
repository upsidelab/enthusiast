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

**Assumed deployment model: one plugin per agentcore instance.** The primary use case is a single vertical (e.g. enthusiast for e-commerce) installed on top of agentcore. Mixing unrelated verticals (e.g. e-commerce + healthcare) on one instance is technically possible via the settings lists but is not a design goal and has not been thought through (e.g. builder routing, DataSet ownership).

> **Open question:** Should agentcore explicitly support multi-plugin deployments? A large enterprise may want multiple domain plugins on one instance (e.g. separate DataSets per department, each with a different plugin). This would require a builder routing mechanism (which builder handles which agent/DataSet). Deferred — not in scope for the initial extraction?.

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
                          # Depends on agentcore-common (extends its interfaces).
    enthusiast/           # Django app — Product, Document, tools, builder, injector
    enthusiast-agent-*/   # Agent plugins
    enthusiast-source-*/  # Source sync plugins (Medusa, Shopify, etc.)
```

Dependency graph:

```
agentcore-common          # pure framework interfaces, no domain knowledge
       ↑
enthusiast-common         # extends agentcore-common with e-commerce types
       ↑
enthusiast (Django app)   # wires it all together
```

`enthusiast-common` depends on `agentcore-common`. E-commerce interfaces extend the framework interfaces — for example, `BaseProductRetriever` extends `BaseVectorStoreRetriever` from agentcore-common. Each layer knows only what it needs to; agentcore-common stays pure.

---

## Migrations

Plugin models live in the plugin's own Django app and define their own migrations. When a plugin is added to `INSTALLED_APPS`, Django's standard migration system picks them up automatically — no special mechanism needed.

```bash
# After adding enthusiast to INSTALLED_APPS:
python manage.py migrate          # applies agentcore + enthusiast migrations together
python manage.py makemigrations   # generates new migrations for any plugin model change
```

Each plugin ships its own `migrations/` directory. agentcore's migrations and plugin migrations are independent and applied in the correct order via Django's dependency graph (`dependencies = [('agentcore', '0001_initial')]` in the plugin migration).

---

## DomainEntity

`DomainEntity` is a pure Python ABC in `agentcore-common` (zero Django dependency). Plugin models inherit from it alongside `models.Model` to declare themselves as visible in the agentcore UI and API.

```python
# enthusiast/models/product.py
from agentcore_common.entities import DomainEntity, EntityField

class Product(DomainEntity, models.Model):
    dataset = models.ForeignKey('agentcore.DataSet', on_delete=models.CASCADE)
    sku = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    price = models.DecimalField(...)

    class EntityMeta:
        slug = 'products'
        label = 'Products'
        list_fields = [
            EntityField('sku', label='SKU'),
            EntityField('name', label='Product Name'),
            EntityField('price', label='Price'),
        ]
```

**Design decisions:**

- **`EntityMeta` inner class** — mirrors Django's `Meta` convention, keeps namespace clean
- **`EntityField` objects** — not plain strings; carries `label` for UI rendering
- **Read-only** — list endpoint only (`GET /api/datasets/{id}/products/`), no detail view, no write operations; write goes through Integration/sync engine
- **Pagination** — automatic via DRF global settings; no filtering (YAGNI)
- **Dynamic serializer** — agentcore builds a `ModelSerializer` via `type()` once at startup in `AppConfig.ready()`, cached in entity registry; no per-entity serializer needed
- **Frontend discovery** — `GET /api/entities/` returns entity definitions (slug, label, fields); React renders a generic `EntityTable` component per entity — zero frontend work per plugin

**Registration** — via settings list, consistent with all other plugin registration in the project:

```python
# settings_override.py
AGENTCORE_ENTITY_PLUGINS = [
    'enthusiast.models.Product',
    'enthusiast.models.Document',
]
```

**Settings prefix** — all agentcore settings use `AGENTCORE_*` prefix. The current `CATALOG_*` prefix disappears after the split — it is an e-commerce concept, not a framework concept.

---

## Frontend

agentcore ships a React UI for chat, DataSet management, Integration configuration, and **entity tables** rendered dynamically from `AGENTCORE_ENTITY_PLUGINS` via `GET /api/entities/`. Plugin-specific UI beyond generic tables (e.g. a multi-step enrichment workflow, custom forms, bulk actions) requires manual frontend development — there is no plugin slot or injection mechanism for React components yet.

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
