# Enthusiast Product Web Scraper Agent

The Product Web Scraper agent accepts one or more product page URLs, fetches and extracts structured product data using an LLM, and upserts the results directly into the configured ecommerce platform. When confirmation mode is enabled (default), the agent presents extracted data to the user and waits for approval before writing to the catalog.

## Installing the Product Web Scraper Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-product-web-scraper
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_product_web_scraper.ProductWebScraperAgent',
]
```

To also register the agentic execution definition, add the following to your config/settings_override.py:

```python
AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [
    'enthusiast_agent_product_web_scraper.ProductWebScraperExecutionDefinition',
]
```
