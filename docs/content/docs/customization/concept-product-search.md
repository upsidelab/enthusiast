---
sidebar_position: 5
---

# Concept: Product Search Agent
This example walks you through building a tool calling agent that searches the product catalog and verifies the results against the user's request. It uses the building blocks that the Enthusiast domain definition adds to Suvereo, described in [E-commerce Agents](/docs/agents/agent-types).

The agent lives in your own Python package, which depends on the Enthusiast and Suvereo packages it builds on:

```toml
dependencies = [
    "suvereo-common",
    "suvereo-agent-tool-calling",
    "enthusiast-domain",
    "enthusiast-domain-tools",
]
```

## Prompt
Start with the system prompt. It tells the agent which tools to use and in what order:

```python
PRODUCT_FINDER_AGENT_PROMPT = """
You're an intelligent assistant that helps the user to find products that fit their needs.
Always start by using the product_examples tool to get a sample of products available in the catalog.
Then, use the search_matching_products tool to find products matching the user's request.
Before you present the results, use the verify_products tool to check that they meet the user's criteria.
When you need more information to refine the search, ask about one attribute at a time.
"""
```

## Tools
Tools subclass `BaseLLMTool` from `suvereo-common`. Each tool has a name, a description and an input schema that the language model uses to call it, and a `run` method. Tools get the e-commerce dependencies through the injector, as `self._injector`, and the language model as `self._llm`.

### Product Search Tool
This tool uses the product retriever to find products matching a natural-language description:

```python
import json

from pydantic import BaseModel, Field
from suvereo_common.tools import BaseLLMTool


class ProductSearchInput(BaseModel):
    product_description: str = Field(description="Product description to search for.")


class ProductSearchTool(BaseLLMTool):
    NAME = "search_matching_products"
    DESCRIPTION = "Use it with suitable phrases when you need to find matching products."
    ARGS_SCHEMA = ProductSearchInput
    RETURN_DIRECT = False

    def run(self, product_description: str) -> str:
        product_retriever = self._injector.product_retriever
        products = product_retriever.find_products_matching_query(product_description)
        if not products:
            return "No products found, try to loosen the criteria"
        return json.dumps(product_retriever.product_details_as_json(products))
```

### Product Verification Tool
This tool asks the language model whether the found products meet the user's criteria:

```python
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from suvereo_common.tools import BaseLLMTool

VERIFY_PRODUCTS_PROMPT = """
Check which of the following products meet the criteria described below.
Respond with the products that meet them, and explain why the others don't.

Criteria: {criteria}

Products: {products}
"""


class ProductVerificationInput(BaseModel):
    criteria: str = Field(description="The user's criteria for the product.")
    products: str = Field(description="The products to verify, as returned by the search.")


class ProductVerificationTool(BaseLLMTool):
    NAME = "verify_products"
    DESCRIPTION = "Use it to verify that the products you found meet the user's criteria."
    ARGS_SCHEMA = ProductVerificationInput
    RETURN_DIRECT = False

    def run(self, criteria: str, products: str) -> str:
        chain = PromptTemplate.from_template(VERIFY_PRODUCTS_PROMPT) | self._llm
        return chain.invoke({"criteria": criteria, "products": products}).content
```

## Agent
The agent is a `BaseToolCallingAgent` that uses `EcommerceAgentBuilder`, so its tools can access the product retriever. Besides the two tools above, it uses `ProductExamplesTool` from `enthusiast-domain-tools`, which shows the agent a sample of the catalog:

```python
from enthusiast_domain.builder import EcommerceAgentBuilder
from enthusiast_domain_tools import ProductExamplesTool
from suvereo_agent_tool_calling import BaseToolCallingAgent
from suvereo_common.config.base import LLMToolConfig

from .prompt import PRODUCT_FINDER_AGENT_PROMPT
from .tools import ProductSearchTool, ProductVerificationTool


class ProductFinderAgent(BaseToolCallingAgent):
    AGENT_KEY = "product-finder"
    NAME = "Product Finder"
    SYSTEM_PROMPT = PRODUCT_FINDER_AGENT_PROMPT
    BUILDER_CLASS = EcommerceAgentBuilder
    TOOLS = [
        LLMToolConfig(tool_class=ProductExamplesTool),
        LLMToolConfig(tool_class=ProductSearchTool),
        LLMToolConfig(tool_class=ProductVerificationTool),
    ]
```

To let the agent write its own SQL queries instead, use `ProductSQLSearchTool` from `enthusiast-domain-tools`. The queries are validated before they run, so the agent can only read products from the current data set. This is how the pre-built [Product Search agent](/agents/product-search) works.

## Registering the Agent
Add the agent to `AVAILABLE_AGENTS` in your `settings_override.py`:

```python
AVAILABLE_AGENTS = [
    "your_package.agents.ProductFinderAgent",
]
```

Restart the server, then create an agent of this type in the Suvereo admin UI. Finally, use a [product source integration](/integrations) to load your products into the data set.
