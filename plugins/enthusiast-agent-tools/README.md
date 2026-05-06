# Enthusiast Agent Tools

Shared tools for Enthusiast agents. This package provides reusable tool implementations that multiple agents can depend on directly, rather than pulling them in transitively through other agent plugins.

## Tools

### `UpsertProductDetailsTool`

Creates or updates products in the connected eCommerce platform by SKU. Accepts a batch of products in a single call and records each upsert outcome to the tool scratchpad for downstream validators. Requires an `ECommercePlatformConnector` to be configured on the injector.

### `StopExecutionTool`

Signals that an agentic execution run cannot continue and should halt immediately. The agent provides a `stop_reason` which is surfaced as the execution failure summary. Use only when further progress is impossible — not for retryable failures.

### `ProductExamplesTool`

Returns a sample of products from the catalog to help the agent understand the catalog's structure and terminology before running searches.

### `ProductSQLSearchTool`

Finds products by executing a SQL SELECT query against the `catalog_product` table. Returns matching products as JSON, or a prompt to narrow the criteria when too many results are returned.

## Installation

This package is a dependency of other Enthusiast agent plugins and is typically installed automatically alongside them. To install it directly:

```shell
pip install enthusiast-agent-tools
```

## Usage

Import the tools directly from this package and register them in your agent's `TOOLS` list:

```python
from enthusiast_agent_tools import ProductExamplesTool, ProductSQLSearchTool
from enthusiast_common.config.base import LLMToolConfig

class MyAgent(BaseToolCallingAgent):
    TOOLS = [
        LLMToolConfig(tool_class=ProductExamplesTool),
        LLMToolConfig(tool_class=ProductSQLSearchTool),
    ]
```
