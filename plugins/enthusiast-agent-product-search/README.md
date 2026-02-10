# Enthusiast Product Search Agent

The Product Search agent takes unstructured user requests - anything from a rough idea to a precise query - and filters your product catalog to find relevant matches. When the request is ambiguous or too broad, it asks targeted follow-up questions until it narrows the results to the desired number of products.

## Installing the Product Search Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-product-search
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_product_search.ProductSearchAgent',
]
```