---
sidebar_position: 2
---

# E-commerce Agents

Enthusiast agents are regular [Suvereo agents](https://upsidelab.io/tools/suvereo/docs/agents/agent-classes). They subclass `BaseToolCallingAgent` from `suvereo-agent-tool-calling` and are registered in `AVAILABLE_AGENTS`, like any other agent. What makes them e-commerce agents is the builder they use, which gives their tools access to the catalog and to your e-commerce platform.

This page describes what the Enthusiast domain definition adds on top of Suvereo. For the agent contract itself (class variables, prompts, memory, tool configuration), see the [Suvereo agent documentation](https://upsidelab.io/tools/suvereo/docs/agents/agent-architecture).

## The E-commerce Builder

An agent selects its builder with the `BUILDER_CLASS` class variable. All pre-built Enthusiast agents use `EcommerceAgentBuilder` from `enthusiast-vertical`:

```python
from enthusiast_vertical.builder import EcommerceAgentBuilder
from enthusiast_vertical_tools import ProductExamplesTool, ProductSQLSearchTool
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig

from .prompt import PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT


class ProductSearchAgent(BaseToolCallingAgent):
    AGENT_KEY = "enthusiast-agent-product-search"
    NAME = "Product Search"
    SYSTEM_PROMPT = PRODUCT_SEARCH_TOOL_CALLING_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    TOOLS = [
        LLMToolConfig(tool_class=ProductSQLSearchTool),
        LLMToolConfig(tool_class=ProductExamplesTool),
    ]
```

`EcommerceAgentBuilder` extends Suvereo's `AgentBuilder`. In addition to everything the default builder provides (chat history, memory, repositories), it creates an `EcommerceInjector` that exposes three e-commerce dependencies to the agent's tools.

## The E-commerce Injector

Tools receive the injector when they are created and access it as `self._injector`. `EcommerceInjector` extends Suvereo's [injector](https://upsidelab.io/tools/suvereo/docs/agents/injector) with:

| Property | Type | Purpose |
|---|---|---|
| `product_retriever` | `ProductRetriever` | Looks up products in the current data set |
| `document_retriever` | `DocumentRetriever` | Semantic search over the documents in the current data set |
| `ecommerce_platform_connector` | `ECommercePlatformConnector` or `None` | Performs actions in the e-commerce platform configured for the data set |

### Product Retriever

`ProductRetriever` reads from the domain definition's product table, always limited to the current data set:

- `find_products_with_sql(sql_query)`: runs a `SELECT` query written by the agent. The query is validated before it runs: it may only read the product table, and a data set condition is added automatically.
- `find_products_matching_query(user_query)`: asks the language model to build the query from a natural-language description.
- `get_sample_products_json()`: returns a sample of products, which helps the agent understand the catalog's structure before searching it.
- `product_details_as_json(products)`: serializes products for the agent.

### Document Retriever

`DocumentRetriever` performs vector search over document chunks. `find_content_matching_query(query)` returns the chunks most relevant to the query, using the embedding model configured for the data set.

### E-commerce Platform Connector

The connector is resolved from the data set's **E-Commerce system** integration (for example [Medusa](/integrations/medusa)). When no such integration is configured, the property is `None`, and tools should tell the user to configure one:

```python
connector = self._injector.ecommerce_platform_connector
if not connector:
    return "The user needs to configure an ecommerce platform connector first"
order_id = connector.create_order_with_items(items)
```

`ECommercePlatformConnector` (from `enthusiast-vertical-common`) provides operations such as `create_order_with_items`, `get_product_by_sku`, `create_product`, `update_product`, `update_stock` and `get_admin_url_for_order_id`.

## Shared Tools

The `enthusiast-vertical-tools` package contains tools used by several pre-built agents, which you can also use in your own agents:

| Tool | Purpose |
|---|---|
| `ProductExamplesTool` | Returns a sample of products, so the agent can learn the catalog's structure |
| `ProductSQLSearchTool` | Lets the agent search the catalog with a SQL `SELECT` query |
| `UpsertProductDetailsTool` | Creates or updates a product in the e-commerce platform |

To add one to an agent, list it in `TOOLS`:

```python
TOOLS = [
    LLMToolConfig(tool_class=ProductExamplesTool),
    LLMToolConfig(tool_class=ProductSQLSearchTool),
]
```

## Next Steps

- [Concept: Product Search Agent](/docs/customization/concept-product-search) walks through building an e-commerce agent step by step.
- [Pre-built Agents](/agents) lists the agents that ship with Enthusiast.
- [Creating a Custom Agent](https://upsidelab.io/tools/suvereo/docs/customization/custom-agent) in the Suvereo documentation covers the general agent workflow.
