# Enthusiast Catalog Enrichment Agent

The Catalog Enrichment agent processes unstructured vendor product sheets - PDFs, scans, or raw text - and extracts product attributes and details for use in your catalog. It can be customized per category to pull different attribute sets and can flag unclear or missing information, triggering a human-in-the-loop step when clarification is required.

## Installing the Catalog Enrichment Agent

Run the following command inside your application directory:
```commandline
poetry add enthusiast-agent-catalog-enrichment
```

Then, register the agent in your config/settings_override.py.

```python
AVAILABLE_AGENTS = {
    "enthusiast-agent-catalog-enrichment": {
        "name": "Catalog Enrichment",
        "agent_directory_path": "enthusiast_agent_catalog_enrichment"
    },
}
```