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

## What agentcore Owns

agentcore is a pure AI agent framework. It knows nothing about products, documents, or e-commerce. It provides:

- **DataSet** — the central tenant concept. Holds LLM config, embedding config, and is the anchor all plugin models reference via FK. Replaces the current Workspace.
- **Conversation / Message / Agent** — core conversation management
- **AgenticExecution** — autonomous multi-step task execution with retries
- **ToolCallingAgent** — a generic tool-calling agent shipped out of the box. No built-in tools — plugins register tools via settings.
- **Integration** — a single external system connection per DataSet (e.g. Medusa, Shopify). Type and config defined by the plugin. Configured in the UI.
- **LLM provider plugins** — OpenAI, Anthropic, Google, Mistral, Ollama, Azure
- **WebSocket streaming, memory strategies, React chat UI, REST API**

---

## What enthusiast Owns

enthusiast is the e-commerce vertical. It adds:

- **Product / Document models** — with FK to `agentcore.DataSet`
- **Sync engine** — pulls products and documents from Medusa, Shopify, etc. and stores embeddings
- **E-commerce tools** — ProductSearchTool, DocumentSearchTool, OrderManagementTool
- **AgentBuilder + Injector** — wires up e-commerce retrievers and tools for the agent
- **Source plugins** — `enthusiast-source-medusa`, `enthusiast-source-shopify`, etc.
- **Agent plugins** — ProductSearchAgent, CatalogEnrichmentAgent, OrderIntakeAgent, etc.

agentcore knows nothing about products or documents. That's enthusiast's domain.

---

## Plugin System

Plugins register with agentcore via `settings_override.py`. One mechanism, no magic:

```python
# settings_override.py
INSTALLED_APPS += ['enthusiast']

AGENTCORE_BUILDER_PLUGINS  = ['enthusiast.builder.EnthusiastAgentBuilder']
AGENTCORE_TOOL_PLUGINS     = ['enthusiast.tools.ProductSearchTool', ...]
AGENTCORE_AGENT_PLUGINS    = ['enthusiast_agent_product_search.ProductSearchAgent', ...]
AGENTCORE_INTEGRATION_PLUGINS = ['enthusiast.integrations.MedusaIntegration', ...]
```

agentcore reads these lists at startup and loads the declared classes. No `AppConfig.ready()` registration calls.

---

## Integration Model

Each DataSet has one Integration — a connection to an external system. The plugin defines the Integration type by extending `BaseIntegration`:

```python
class MedusaIntegration(BaseIntegration):
    type = 'medusa'
    label = 'Medusa'

    def get_config_schema(self): ...   # fields for the UI form
    def test_connection(self, config): ...
    def get_client(self, config): ...
```

agentcore renders a generic config form in the UI based on the schema the plugin provides. Integration credentials (e.g. Medusa API key) are stored per-DataSet in the database — not in env vars, because each DataSet connects to a different store.

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
- **Frontend for rich plugin UI** — agentcore's generic UI covers DataSet, Integration, chat. Whether enthusiast needs a richer Catalog view (products grid, document browser) is deferred. Consult with Filip before any frontend work begins.
