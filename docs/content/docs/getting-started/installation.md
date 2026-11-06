# Installation

> [!NOTE]
> Looking for the Enthusiast 1.7 installation guide? It is available [here](https://upsidelab.io/tools/enthusiast/v1.7/docs/getting-started/installation).

Enthusiast is the e-commerce [domain definition](https://upsidelab.io/tools/suvereo/docs/customization/domain-onboarding) for [Suvereo](https://upsidelab.io/tools/suvereo/docs). Suvereo provides the platform (conversations, agentic executions, language models, users and the admin UI), and Enthusiast is installed on top of it as a set of Python packages.

## Prerequisites

You need a running Suvereo instance. Follow the [Suvereo installation guide](https://upsidelab.io/tools/suvereo/docs/getting-started/installation) to set one up, then come back here.

## Installing the Packages

Enthusiast is split into packages, so you can install only what you need:

| Package | Purpose |
|---|---|
| `enthusiast-vertical` | The domain definition itself: product and document entities, migrations, retrievers and sync managers. Always required. |
| `enthusiast-source-*` | Product and document sources, and e-commerce store integrations. See [Integrations](/integrations). |
| `enthusiast-agent-*` | Pre-built agents. See [Pre-built Agents](/agents). |

Run the following command inside your application directory. To get started, install the domain definition together with the sample data source and the Product Search agent:

```bash
poetry add enthusiast-vertical enthusiast-source-sample enthusiast-agent-product-search
```

## Configuring Suvereo

Register the domain definition and its plugins in your `config/settings_override.py`:

```python
INSTALLED_DOMAIN_DEFINITIONS = ["enthusiast_vertical"]

CATALOG_ENTITY_PLUGINS = [
    "enthusiast_vertical.models.Product",
    "enthusiast_vertical.models.Document",
]

CATALOG_INTEGRATION_MANAGERS = [
    "enthusiast_vertical.sync.ProductSourceManager",
    "enthusiast_vertical.sync.DocumentSourceManager",
    "enthusiast_vertical.sync.ECommerceIntegrationManager",
]

CATALOG_INTEGRATION_PLUGINS = [
    "enthusiast_source_sample.SampleProductSource",
    "enthusiast_source_sample.SampleDocumentSource",
]

AVAILABLE_AGENTS = [
    "enthusiast_agent_product_search.ProductSearchAgent",
]
```

Each integration and agent page lists the exact entry to add when you install more of them.

## Applying Migrations

The domain definition ships its own database migrations. Apply them after installing it:

```bash
./manage.py migrate
```

If you run Suvereo with Docker Compose and `RUN_MIGRATIONS=True`, migrations are applied automatically when the server starts.

Then, restart the server so the domain definition and its plugins become available.

You can now [import test data](/docs/getting-started/import-test-data).
