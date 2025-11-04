<div align="center">
  <a href="https://upsidelab.io/tools/enthusiast" />
    <img src="https://github.com/user-attachments/assets/966204c3-ff69-47b2-a247-9f9cfa4e5b7d" height="150px" alt="Enthusiast">
  </a>
</div>

<h1 align="center">enthusiast.</h1>

<p align="center">Production-ready Agentic AI Toolkit for E-commerce.</p>
<div align="center">
  <strong>
    <a href="https://upsidelab.io/tools/enthusiast">Website</a> |
    <a href="https://upsidelab.io/tools/enthusiast/docs/getting-started/installation">Installation Guide</a> |
    <a href="https://upsidelab.io/tools/enthusiast/docs">View Docs</a> |
  </strong>
</div>

&nbsp;

[Enthusiast](https://upsidelab.io/tools/enthusiast) is an open-source, customizable agentic AI toolkit for building AI agents that automate e‑commerce workflows and human-intensive back‑office tasks. It combines retrieval‑augmented generation (RAG), vector search, and workflow orchestration to give teams a turnkey starting point to build custom AI agents grounded in their product data and processes — agents that can run in minutes and scale to production.

Enthusiast gives you full control over infrastructure, data, models, prompts, and integrations. You can run it locally with Docker, deploy to Kubernetes, or host it on-premise. Its model-agnostic architecture supports both cloud-based models like OpenAI and Gemini, and self-hosted deployments such as Mistral, Ollama, or DeepSeek.

## Why use Enthusiast?

Building reliable, e-commerce AI tools is hard — especially when you need them to reason over complex product catalog, stay grounded in source data, and integrate into existing e-commerce systems.

Enthusiast is a **customizable AI backbone** to help teams cut down time, cost, and integration overhead by providing ready-to-customize foundation and pre-built agents for building e-commerce AI workflows with minimal effort.

Some key highlights include:

- **[Customizable by design](https://upsidelab.io/tools/enthusiast/docs/customization/system-architecture/)** - Built with Python (Django) and React, Enthusiast exposes clear interfaces for adding custom agents or tools in Python, or creating new data connectors without forking the core platform — making it ideal for building unique workflows and rapid prototyping.

- **[Pre-built agents for common workflows](https://upsidelab.io/tools/enthusiast/agents/)** - Enthusiast ships with ready‑to‑use agents for product search, catalog enrichment, content generation, and support Q&A. Easily extend or adapt them to match your processes.

- **[Model-agnostic architecture](https://upsidelab.io/tools/enthusiast/integrations#Language%20Models)** - Swap between providers or models via configuration without altering application logic. Enthusiast works well with commercial APIs or open‑weight models (OpenAI, Azure, Gemini, Mistral, Ollama), helping you future-proof your AI stack.

- **Deploy to cloud or on-premise** - Deploy on your own infrastructure using Docker Compose or scale it in production on Kubernetes. Full control over infrastructure and data.

- **[E-commerce integrations included](https://upsidelab.io/tools/enthusiast/integrations/)** - Native connectors to synchronize your catalogs from platforms like Medusa.JS, Shopify, Shopware or Solidus without extra integration work. A plugin system also lets you write your own product or document sources.

## Getting Started

The recommended way to get started with Enthusiast is with Docker by following these steps:

1. **Clone this repository**

```bash
git clone https://github.com/upsidelab/enthusiast-starter
```

2. **Copy sample env**

```bash
cp config/env.sample config/env
```

3. **Add your OpenAI key or configure another LLM** ([See Integrations](https://upsidelab.io/tools/enthusiast/integrations/)).

```
OPENAI_API_KEY=...
```

4. **Start the Enthusiast services**

```bash
docker compose build && docker compose up
```

For detailed instructions, see the [installation guide](https://upsidelab.io/tools/enthusiast/docs/getting-started/installation/) in the docs.

### Pre‑built Agents

Enthusiast ships with ready‑to‑use agents for the most common e‑commerce back‑office challenges out of the box. Use them as‑is or as templates for your own workflows.

- **[Product Search Agent](https://upsidelab.io/tools/enthusiast/agents/agent-product-search/)** - Provides AI-powered product search across your catalog using vector embeddings, enabling natural-language queries like “Show me waterproof jackets under $100,” and the agent returns verifiable results from your indexed catalog.

- **[User Manuals Agent](https://upsidelab.io/tools/enthusiast/agents/agent-customer-support/)** - Provides precise answers from technical documentation and manuals using retrieval-augmented generation to keep responses accurate and grounded in source content.

- **[OCR to Order Agent](https://upsidelab.io/tools/enthusiast/agents/agent-ocr-order/)** - Converts unstructured documents (like scanned invoices or PDFs) into structured purchase orders and validates data against your catalog before passing it downstream.

- **[Product Catalog Enrichment Agent](https://upsidelab.io/tools/enthusiast/agents/agent-catalog-enrichment/)** - Generate product descriptions, attributes, or translations directly from your data. Validation agents confirm factual accuracy prior to publication.

Each agent is available as a separate package and can be installed via `poetry add`. See the [Pre-built Agents](https://upsidelab.io/tools/enthusiast/agents/) documentation for installation instructions, use-cases, and customization.

## E-commerce Integrations

Enthusiast integrates seamlessly with popular e-commerce and data platforms, letting you deploy AI-powered automation without changing your existing stack.

Supported integrations include: Medusa, Shopify, Shopware, WooCommerce, Solidus.

<img width="600" alt="Integrations" src="https://github.com/user-attachments/assets/84d1f4d1-51ac-4c6c-8412-a037f7ce4ecd" />

It can also be integrated with CMS systems such as Sanity and WordPress.

## Built by Upside

Upside is a full-stack digital agency that builds robust, secure, and fully compliant AI-powered solutions — from data platforms and healthcare solutions to e-commerce systems — for startups and enterprise businesses.

### Want to see Enthusiast in action?

[**Book a live demo**](https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ3NyFdPn_jqYqD24asveLkfrB1NTal0PWkLNHFTT4Fmp6sNW50-0or8WyIzBriF8IFdP1jXSPjQ) to see Enthusiast in action and discuss how we can tailor it to your e-commerce workflows.

## Contributing

We welcome contributions of any kind – new connectors, agents, tools or
bug fixes. See [CONTRIBUTING.md](https://github.com/upsidelab/enthusiast/?tab=contributing-ov-file) for guidelines and open issues.

It's also super helpful if you could leave the project a star to show your support.

If you’re using Enthusiast in production, let us know! We’d love to hear how it’s helping you automate your e-commerce workflows, and feature your use case.

## License

Enthusiast is a fully open-source agentic AI framework that will always remain free under the [MIT License](https://github.com/upsidelab/enthusiast/blob/main/LICENSE.md).
