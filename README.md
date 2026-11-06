<div align="center">
  <a href="https://upsidelab.io/tools/enthusiast" />
    <img src="https://github.com/user-attachments/assets/966204c3-ff69-47b2-a247-9f9cfa4e5b7d" height="150px" alt="Enthusiast">
  </a>
</div>

<h1 align="center">enthusiast.</h1>

<p align="center">The e-commerce domain definition for the Suvereo agentic AI framework.</p>
<div align="center">
  <strong>
    <a href="https://upsidelab.io/tools/enthusiast">Website</a> |
    <a href="https://upsidelab.io/tools/enthusiast/docs/getting-started/installation">Installation Guide</a> |
    <a href="https://upsidelab.io/tools/enthusiast/docs">View Docs</a>
  </strong>
</div>


## Introduction
[Enthusiast](https://upsidelab.io/tools/enthusiast) is the open-source e-commerce domain definition for [Suvereo](https://upsidelab.io/tools/suvereo/docs), an agentic AI framework.

Suvereo provides the platform: conversations, agentic executions, language models, users and permissions, and the admin UI. Enthusiast adds what is specific to e-commerce:

- **Data**: products and documents, indexed for semantic search.
- **Integrations**: product and document sources and e-commerce store connectors (Medusa, Shopify, Shopware, Solidus, WooCommerce, WordPress, Sanity).
- **Agents**: pre-built agents for product search, order intake, catalog enrichment and more.

> Looking for Enthusiast 1.7, the standalone version? See the [Enthusiast 1.7 documentation](https://upsidelab.io/tools/enthusiast/v1.7/docs) and the [v1.7.1 release](https://github.com/upsidelab/enthusiast/tree/v1.7.1).

## Getting Started
Enthusiast is installed into a Suvereo instance as a set of Python packages:
1. Set up Suvereo (see the [Suvereo installation guide](https://upsidelab.io/tools/suvereo/docs/getting-started/installation)).
2. Install the domain definition and the integrations and agents you need, and register them in Suvereo's settings (see the [installation guide](https://upsidelab.io/tools/enthusiast/docs/getting-started/installation)).

You can also book a [live demo](https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ3NyFdPn_jqYqD24asveLkfrB1NTal0PWkLNHFTT4Fmp6sNW50-0or8WyIzBriF8IFdP1jXSPjQ) to see it in action.

## Example use cases

- [**AI-Based Product Discovery**](https://upsidelab.io/tools/enthusiast/agents/product-search) Enable natural-language product search. Users describe requirements in plain terms, and the agent retrieves results from your indexed catalog.

- [**User Manual Search**](https://upsidelab.io/tools/enthusiast/agents/user-manual-search) Provide precise answers from technical documentation and manuals.

- [**Order Intake**](https://upsidelab.io/tools/enthusiast/agents/order-intake) Convert unstructured inputs — such as scanned purchase order documents or notes - into e-commerce orders.

- [**Product Catalog Enrichment**](https://upsidelab.io/tools/enthusiast/agents/catalog-enrichment) Extract product descriptions, attributes, or translations from unstructured product sheets.

- [**Catalog Web Import**](https://upsidelab.io/tools/enthusiast/agents/catalog-web-import) Import product data directly from supplier or distributor web pages.

- [**Invoice Scanning**](https://upsidelab.io/tools/enthusiast/agents/invoice-scanning) Extract line items from supplier invoices and update stock levels in your e-commerce platform.

## Packages

All packages live in [`plugins/`](plugins) and are published to PyPI:

| Package | Purpose |
|---|---|
| `enthusiast-vertical-common` | E-commerce interfaces and data types (product, document and e-commerce integration plugins, platform connector). No Django dependency. |
| `enthusiast-vertical` | The domain definition's Django app: product and document models and migrations, retrievers, sync managers. |
| `enthusiast-vertical-tools` | Agent tools shared by the pre-built agents. |
| `enthusiast-source-*` | Integrations: Medusa, Shopify, Shopware, Solidus, WooCommerce, WordPress, Sanity, and sample data. |
| `enthusiast-agent-*` | Pre-built agents. |

## Pre-built Integrations

Connect to your e-commerce stack in minutes, with minimal configuration required.

<a href="https://upsidelab.io/tools/enthusiast/integrations"><img width="600" alt="Integrations" src="https://github.com/user-attachments/assets/84d1f4d1-51ac-4c6c-8412-a037f7ce4ecd" /></a>

## License

Enthusiast is fully open-source and will always remain free under the [MIT License](https://github.com/upsidelab/enthusiast/blob/main/LICENSE.md).
