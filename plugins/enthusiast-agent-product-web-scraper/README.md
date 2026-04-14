# enthusiast-agent-product-web-scraper

Product Web Scraper Agent for [Enthusiast](https://github.com/upsidelab/enthusiast).

Fetches product data from web page URLs, extracts structured product fields using an LLM,
and upserts the results into the configured ecommerce platform.

## Installation

```bash
pip install enthusiast-agent-product-web-scraper
```

## Registration

Add to your Django settings:

```python
AVAILABLE_AGENTS = [
    ...
    "enthusiast_agent_product_web_scraper.ProductWebScraperAgent",
]
```
