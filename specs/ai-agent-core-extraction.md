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
- **Integration** — one connection per integration type per DataSet (type and config defined by the plugin, configured in the UI)
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
│    AGENTCORE_*_PLUGINS  ─────────────────┼──┼──► loads classes
│    (agents, builder, integrations,       │  │
│     agentic executions, entities)        │  │
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
    │  reads AGENTCORE_BUILDER_PLUGINS → loads EnthusiastAgentBuilder
    ▼
BaseAgentBuilder.build() (agentcore)
    │  resolves LLM from dataset, builds the agent's tools,
    │  instantiates the ToolCallingAgent
    │  delegates the injector to the vertical:
    ▼
EnthusiastAgentBuilder.build_injector() (enthusiast)
    │  builds ProductRetriever, DocumentRetriever + connector
    ▼
ToolCallingAgent (agentcore)
    │  LangChain tool-calling loop
    │  calls ProductSearchTool.run(query)
    ▼
ProductSearchTool (enthusiast)
    │  vector search on ProductContentChunk via pgvector
    │  returns results
    ▼
LLM generates response → WebSocket → User
```

---

## How a Vertical Plugin Works

A plugin is responsible for three things:

**1. Domain Models — the domain knowledge**

The plugin defines its own models with a FK to `agentcore.DataSet`. agentcore is unaware of their structure — the plugin owns the models, the sync logic, and the mapping of external data onto those models. It declares *what* text to index per entity (`get_indexable_content()`); the chunking, embedding, and vector storage are handled by agentcore's indexing pipeline (see [Sync & Indexing](#sync--indexing)).

Plugin models declare themselves as `DomainEntity` (see [DomainEntity](#domainentity)), which makes them automatically visible in the agentcore UI as read-only tables — no extra frontend work needed per plugin.

| Vertical | Domain Models |
|---|---|
| enthusiast (e-commerce) | Product, Document |

**2. Integration — the external system**

A DataSet can have multiple integrations — one per type (e.g. Medusa + Shopify on the same DataSet). The plugin defines the Integration type:

```python
# agentcore-common
class BaseIntegration:
    type: str
    label: str

    def get_config_schema(self): ...   # drives the UI config form
    def test_connection(self, config): ...
    def sync(self, dataset_id): ...    # agentcore calls this on "Sync" action

# enthusiast-common
class ECommerceIntegrationPlugin(BaseIntegration):
    def build_connector(self) -> ECommercePlatformConnector: ...

# enthusiast
class MedusaIntegration(ECommerceIntegrationPlugin):
    type = 'medusa'
    label = 'Medusa'

    def get_config_schema(self): ...
    def test_connection(self, config): ...
    def sync(self, dataset_id): ...       # pulls products, indexes them via agentcore
    def build_connector(self) -> MedusaPlatformConnector: ...
```

**Design decisions:**

- **Integration lifecycle** — agentcore stores integration config (URL, API key, etc.) as JSON in the `Integration` model. Before calling any method on an integration, agentcore loads the DB record, resolves the plugin class from `AGENTCORE_INTEGRATION_PLUGINS`, and instantiates it with the stored config. The instance is stateful — config lives on `self`, not passed as a parameter. This is consistent with the current `CONFIGURATION_ARGS` pattern.
- **Sync trigger** — `BaseIntegration` exposes `sync(dataset_id)`. agentcore UI shows a generic "Sync" button per integration and calls this method on a freshly instantiated plugin. The plugin owns *what* gets synced and *where* it is pulled from; the indexing of that data (chunking, embeddings, vector storage) runs through agentcore's pipeline — see [Sync & Indexing](#sync--indexing).
- **Connector access in tools** — `build_connector()` is not on `BaseIntegration`; it lives on `ECommerceIntegrationPlugin` in enthusiast-common. `EnthusiastAgentBuilder` instantiates the integration plugin with config (same lifecycle as above) and calls `build_connector()`. The resulting connector is passed to `EnthusiastInjector`, which exposes it as `ecommerce_platform_connector`. Tools access it via the injector — `self.injector.ecommerce_platform_connector`. `BaseInjector` in agentcore-common has no connector property; it remains domain-agnostic.
- **One integration per type per DataSet** — the uniqueness key is `(DataSet, type)`. A DataSet can hold Medusa + Shopify, but not two Medusa integrations. This is a deliberate tightening over today's model, where a DataSet can hold N product sources of the same kind. Consequence to be aware of: if two integrations both expose a connector (Medusa + Shopify), the builder has no rule yet for *which* connector a tool like `OrderManagementTool` should use. For the initial extraction we assume **at most one connector-capable integration is active per DataSet**; multi-connector routing (a tool selecting a connector by type) is deferred along with the multi-plugin question.
- **Integration vs `enthusiast-source-*` packages** — these are not competing concepts. An `Integration` (e.g. `MedusaIntegration`) is the thin agentcore-facing adapter: it declares the type, config schema, and the `sync()`/`build_connector()` entry points. The heavy lifting — API client, pagination, request/response mapping — lives in its `enthusiast-source-*` package (e.g. `enthusiast-source-medusa`), which the Integration delegates to. This replaces today's split where a source and an integration were separate registered plugins.
- **Inheritance over capabilities — for now** — `BaseIntegration` → `ECommerceIntegrationPlugin` is a simple two-level hierarchy: sync lives on the base, the connector is added by the e-commerce subclass. This is enough while there are only two roles (sync, connector). It does carry a known smell: sync and the connector are really *independent* capabilities, and the current `ECommerceIntegrationPlugin` already glues them via `build_product_source()` delegation. If a third role appears (e.g. webhook/push ingestion, or read-only analytics integrations), this hierarchy starts to strain.

> **Open question (deferred):** Replace inheritance with a capability/mixin model — `BaseIntegration` + `SyncCapability` + `ConnectorCapability`, composed per integration. agentcore would introspect capabilities (`isinstance`) to decide which UI/behavior to expose (Sync button only for `SyncCapability`, connector available to tools only for `ConnectorCapability`). This handles sync-only (CSV), connector-only, and both, and scales to future roles without touching the hierarchy. Not needed for the initial extraction — can be adopted later without rewriting agentcore.

**3. AgentBuilder + Tools — how the agent is assembled**

The plugin provides a builder that wires up its repositories and tools into an agent that agentcore can run:

```python
class EnthusiastAgentBuilder(BaseAgentBuilder):
    # agentcore's BaseAgentBuilder handles LLM, tools, and agent instantiation.
    # the vertical only supplies its domain injector:
    def build_injector(self, dataset, conversation) -> EnthusiastInjector:
        # reads embedding config from dataset → builds product + document retrievers
        # loads Integration from DB → builds ECommercePlatformConnector
        # returns EnthusiastInjector(retrievers=..., connector=...)
        ...
```

See [Agents, Builder & Tools](#agents-builder--tools) for how the agent, its tools, and the builder compose.

---

## Plugin Registration

Plugins register with agentcore via `settings_override.py`:

```python
# settings_override.py
INSTALLED_APPS += ['enthusiast']

AGENTCORE_AGENT_PLUGINS             = ['enthusiast_agent_product_search.ProductSearchAgent', ...]
AGENTCORE_BUILDER_PLUGINS           = ['enthusiast.builder.EnthusiastAgentBuilder']
AGENTCORE_INTEGRATION_PLUGINS       = ['enthusiast.integrations.MedusaIntegration', ...]
AGENTCORE_AGENTIC_EXECUTION_PLUGINS = ['enthusiast_agent_catalog_enrichment.CatalogEnrichmentAgenticExecutionDefinition', ...]
AGENTCORE_ENTITY_PLUGINS            = ['enthusiast.models.Product', 'enthusiast.models.Document']
# Tools are not registered here — each agent declares its own TOOLS (see "Agents, Builder & Tools").
```

agentcore reads these lists at startup and loads the declared classes. One mechanism, no magic.

**Assumed deployment model: one plugin per agentcore instance.** The primary use case is a single vertical (e.g. enthusiast for e-commerce) installed on top of agentcore. Mixing unrelated verticals (e.g. e-commerce + healthcare) on one instance is technically possible via the settings lists but is not a design goal and has not been thought through (e.g. builder routing, DataSet ownership).

> **Open question:** Should agentcore explicitly support multi-plugin deployments? A large enterprise may want multiple domain plugins on one instance (e.g. separate DataSets per department, each with a different plugin). This would require a builder routing mechanism (which builder handles which agent/DataSet). Deferred — not in scope for the initial extraction?.

---

## What enthusiast Brings

enthusiast is the reference implementation of a vertical plugin:

- **Product / Document models** — with FK to `agentcore.DataSet`
- **Sync engine** — pulls data from Medusa, Shopify, etc. and hands each item to agentcore's indexer
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

## Sync & Indexing

Sync is where a vertical's data gets pulled from an external system and turned into searchable knowledge. The key design choice: **the plugin owns *what* and *from where*; agentcore owns the indexing pipeline (*how* text becomes vectors).**

### Why the indexing pipeline lives in agentcore

Today the embedding pipeline (`DataSetObjectEmbeddingsGenerator` in `catalog/services.py`) is already domain-agnostic: it splits text into chunks (`TokenTextSplitter`), resolves the embedding provider from the DataSet's config (`embedding_model`, `embedding_vector_dimensions`, `embedding_chunk_size`, `embedding_chunk_overlap`), generates vectors, and stores them in pgvector. The only domain-specific parts are two lines: which text to index (`Product.get_content()` → `name + description`) and which chunk model it lands in.

This pipeline — token splitting, provider abstraction, vector storage — is the most valuable and hardest-to-get-right piece of an AI agent platform. It is exactly the "infrastructure all verticals share." If each vertical re-implemented it, a new domain (healthcare, logistics) would rewrite the entire RAG stack just to index its own data. So it stays in agentcore. A plugin declares one method and gets the whole pipeline for free.

### Division of responsibility

| Layer | Owns |
|---|---|
| **agentcore** | Trigger (UI/API), Celery task queuing, the indexing pipeline (chunk → embed via DataSet's provider → store in pgvector), the query-embedding + retrieval scaffolding (`BaseVectorStoreRetriever`, see below), embedding-provider plugins. |
| **plugin** | `fetch()`/iterate raw items from the external system, map them onto its own domain models (`update_or_create`), declare *what* text to index per entity, and build its retriever on agentcore's `BaseVectorStoreRetriever`. |

### Indexing — hybrid model

The pipeline logic lives in agentcore, but the **chunk tables stay on the plugin side** with a FK to the domain model. This keeps vector search able to filter by domain fields (e.g. "similar products, but only where `price < 100`" — price lives on `Product`, not on the chunk). The alternative — one generic vector table in agentcore — is simpler but loses that domain-field filtering, so it is not chosen.

- agentcore provides an abstract `BaseEmbeddingChunk` (`content` + `embedding: VectorField`) and the `index_entity()` pipeline helper.
- The plugin's chunk models (`ProductContentChunk`, `DocumentChunk`) inherit `BaseEmbeddingChunk` and add the FK to their domain model. One small migration per indexed entity.
- The entity declares its indexable content (replaces today's `get_content()`):

```python
class Product(DomainEntity, models.Model):
    def get_indexable_content(self) -> str:
        return f"{self.name} {self.description}"   # the only domain-specific line
```

### Vector search — where the boundary sits

agentcore does **not** own a generic cross-domain search endpoint. The split mirrors indexing:

- **agentcore** turns a query string into a vector (same DataSet provider that produced the stored vectors) and provides `BaseVectorStoreRetriever` — the retrieval scaffolding (distance helper, top-k, the provider wiring).
- **the plugin** runs the actual query. Because the chunk tables and their domain FKs live plugin-side, the plugin's `ProductRetriever` (extending `BaseVectorStoreRetriever`) issues the pgvector query against `ProductContentChunk` and can join/filter on `Product` fields (e.g. `price < 100`, in-stock only).

So "retrieval scaffolding" means the provider wiring and distance primitives, not a one-size-fits-all search the plugin can't shape. This is exactly why chunk tables stay domain-side (the hybrid model above) — it keeps domain-field filtering in the plugin's hands.

### Sync flow

A vertical's sync is just: pull raw items, upsert into domain models, hand each to agentcore's indexer.

```python
# enthusiast — MedusaIntegration.sync()
def sync(self, dataset_id):
    for raw in self._fetch_products():                  # plugin: where the data comes from
        product, _ = Product.objects.update_or_create(  # plugin: the domain shape
            dataset_id=dataset_id, entry_id=raw.entry_id, defaults={...},
        )
        index_entity(product)                            # agentcore: chunk + embed + store
```

`index_entity()` reads the DataSet's embedding config off `product.dataset`, splits `get_indexable_content()` into chunks, embeds each via the configured provider, and writes the vectors to the entity's chunk table. The plugin never touches tokenization, providers, or pgvector.

### Triggers

Unchanged from today, just unified under one `Integration`:

- **Manual** — a generic "Sync" button per integration → `POST /api/datasets/{id}/integrations/{int_id}/sync` → queues a Celery task and returns its `task_id`.
- **On create** — creating an integration auto-queues an initial sync (current `perform_create` behavior).

### Out of scope (current limitations, carried forward)

Sync observability is **not** addressed in this extraction — it stays as it is today. A sync returns only a Celery `task_id`; there is no `SyncRun` model, no status/history, no per-run item counts or error tracking, no lock against concurrent syncs of the same integration. Likewise, sync remains **full-fetch**: every run re-fetches everything, re-embeds every fetched item (no content-hash skip), and does not delete stale records or track an incremental cursor. These are known gaps and candidates for future work, but explicitly out of scope here.

---

## Agents, Builder & Tools

These three are easy to confuse because they are always discussed together. They are **layered, not parallel** — an agent declares its tools, and the builder assembles both into a runnable instance.

**Agent — the unit a user picks.** A vertical defines agents as classes that extend agentcore's `ToolCallingAgent`. Each declares its identity (`AGENT_KEY`, `NAME`), the tools it exposes, its prompt, and whether it accepts file uploads:

```python
# enthusiast
class ProductSearchAgent(ToolCallingAgent):
    AGENT_KEY = 'enthusiast-agent-product-search'
    NAME = 'Product Search'
    TOOLS = [LLMToolConfig(tool_class=ProductSearchTool),
             LLMToolConfig(tool_class=ProductExamplesTool)]
```

A user-configured agent is persisted as agentcore's `Agent` model (`agent_type` = `AGENT_KEY`, plus a `config` JSON, `file_upload`, FK to DataSet). A `Conversation` points at one `Agent`, so "which agent answers" resolves via `conversation.agent.agent_type → AGENT_KEY → agent class`.

**Tools — what an agent can do.** Tools are classes (`ProductSearchTool`, `PlaceOrderTool`) the LLM can call. They are declared *by the agent* in its `TOOLS` list — there is **no separate global tool palette**. A tool reaches its dependencies through the injector: `self.injector.product_retriever`, `self.injector.ecommerce_platform_connector`.

**Builder — agentcore's assembly machinery.** Given a configured `Agent` + its `DataSet`, the builder resolves the LLM from DataSet config, builds the domain **injector** (retrievers + connector), constructs the agent's declared tools, and returns a ready-to-run instance. agentcore ships a `BaseAgentBuilder` with the generic orchestration; a vertical subclasses it only to supply its domain injector:

```python
# enthusiast
class EnthusiastAgentBuilder(BaseAgentBuilder):
    def build_injector(self, dataset, conversation) -> EnthusiastInjector:
        # builds product/document retrievers from dataset embedding config,
        # loads Integration → ECommercePlatformConnector,
        # returns EnthusiastInjector(retrievers=..., connector=...)
```

**How they compose at request time:**

```
Conversation → Agent (agent_type)
   → AgentRegistry resolves the agent class + the vertical's builder
   → Builder.build(): LLM + EnthusiastInjector + tools → agent instance
   → agent.get_answer(message) runs the LangChain tool-calling loop
```

**Settings lists — reconciled.** Of the registration lists, agents and the builder each need one; **tools do not**, because an agent already references the tools it uses:

- `AGENTCORE_AGENT_PLUGINS` — agent classes the user can pick (today's `AVAILABLE_AGENTS`).
- `AGENTCORE_BUILDER_PLUGINS` — the vertical's builder (its injector). Typically one per vertical.
- ~~`AGENTCORE_TOOL_PLUGINS`~~ — **redundant** and dropped: tools are referenced by the agents that use them, so they need no separate registration. (Would only be needed for a future "compose an agent from a tool palette in the UI" feature — not in scope.)

---

## AgenticExecution

Alongside interactive chat, agentcore supports **agentic executions** — autonomous, non-interactive runs of an agent against structured input, with an automatic validate-and-retry loop. This already exists today (catalog enrichment, invoice scanning, order intake) and is domain-agnostic infrastructure, so the engine moves to agentcore while the concrete definitions stay in the vertical.

**What stays in agentcore (the engine):**

- `AgenticExecution` model — tracks one run: `agent` FK, `execution_key`, an internal `conversation`, `status` (pending → in_progress → finished | failed), `input`/`result` JSON, `failure_code`, `celery_task_id`.
- `BaseAgenticExecutionDefinition.run()` — the retry loop: call `execute()`, run the validators against the response (and the tool results recorded during the attempt); on a retryable failure, feed the validator's feedback back to the agent and retry up to `MAX_RETRIES`.
- `ToolScratchpad` — a per-run store where tools record their results so validators can inspect them; cleared between retries.
- Base validators, the REST API (`POST /api/agents/{id}/agentic-executions/` + status polling), the Celery task, and the definition registry.

**What the vertical provides (the definitions):**

- Concrete `*AgenticExecutionDefinition` subclasses declaring `EXECUTION_KEY`, `AGENT_KEY`, the Pydantic `INPUT_TYPE`, the domain `VALIDATORS` (e.g. `AllSkusUpsertedValidator`), and the single-attempt `execute()` body.
- Registered via a settings list:

```python
AGENTCORE_AGENTIC_EXECUTION_PLUGINS = [
    'enthusiast_agent_catalog_enrichment.CatalogEnrichmentAgenticExecutionDefinition',
    'enthusiast_agent_invoice_scanning.InvoiceScanningAgenticExecutionDefinition',
]
```

**Relationship to the normal flow:** both interactive chat and agentic executions run through the same `ConversationManager` and the same agent. A `config_type` flag (`CONVERSATION` vs `AGENTIC_EXECUTION_DEFINITION`) lets an agent supply a different system prompt for the autonomous context. An execution drives the agent by calling `conversation.ask()` inside `execute()` — the same tool-calling loop, just run headless with validators gating the result.

---

## Frontend

agentcore ships a React UI for chat, DataSet management, Integration configuration, and **entity tables** rendered dynamically from `AGENTCORE_ENTITY_PLUGINS` via `GET /api/entities/`. Plugin-specific UI beyond generic tables (e.g. a multi-step enrichment workflow, custom forms, bulk actions) requires manual frontend development — there is no plugin slot or injection mechanism for React components yet.

---

## Migration Plan

### Phase 1 — Build agentcore (new repo, green field)
- Extract `enthusiast-common` generic parts → `agentcore-common`
- Rename `enthusiast-model-*` → `agentcore-model-*`
- Move agent infrastructure (Conversation, Agent, AgenticExecution, ConversationManager) → agentcore Django app
- Move the indexing pipeline → agentcore: `Indexer`/`index_entity()`, abstract `BaseEmbeddingChunk`, embedding-provider registry, `BaseVectorStoreRetriever`
- Move the AgenticExecution engine → agentcore: `BaseAgenticExecutionDefinition.run()` retry loop, `ToolScratchpad`, base validators, definition registry, REST API + Celery task
- Add DataSet model (replaces Workspace), Integration model
- agentcore runs standalone with a working chat UI

### Phase 2 — Migrate enthusiast (branch on enthusiast repo)
- Remove everything that moved to agentcore
- Thin `enthusiast-common` to e-commerce structs only
- Implement `EnthusiastAgentBuilder` and `EnthusiastInjector` extending agentcore-common bases
- Product / Document models reference `agentcore.DataSet` via FK
- Chunk models (`ProductContentChunk`, `DocumentChunk`) inherit `BaseEmbeddingChunk`; entities implement `get_indexable_content()` (replaces `get_content()`)
- Port agentic execution definitions + domain validators (catalog enrichment, invoice scanning, order intake) onto the agentcore engine
- Register plugin classes via the `AGENTCORE_*` settings lists (agents, builder, integrations, agentic executions, entities)
- End-to-end: agentcore + enthusiast plugin working together

### Phase 3 — Release
- Publish packages to PyPI
- Reference `docker-compose.yml` with enthusiast pre-installed
- "Build your own vertical" developer guide

---

## Open Questions

- **Final name for agentcore** — placeholder only, needs branding discussion
- **PyPI namespace** — check `agentcore` availability
