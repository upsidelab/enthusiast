# Enthusiast Catalog Web Import Agent

The Catalog Web Import agent accepts one or more product page URLs, fetches and extracts structured product data using an LLM, and upserts the results directly into the configured ecommerce platform. When confirmation mode is enabled (default), the agent presents extracted data to the user and waits for approval before writing to the catalog.

## Installing the Catalog Web Import Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-catalog-web-import
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = [
    'enthusiast_agent_catalog_web_import.CatalogWebImportAgent',
]
```

To also register the agentic execution definition, add the following to your config/settings_override.py:

```python
AVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [
    'enthusiast_agent_catalog_web_import.CatalogWebImportExecutionDefinition',
]
```
