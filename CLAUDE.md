# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enthusiast is the e-commerce vertical for [Suvereo](https://github.com/upsidelab/suvereo), a domain-agnostic agentic AI framework. This repository contains only the vertical: a set of Python packages that a Suvereo installation adds as dependencies and enables in its `settings_override.py` (`INSTALLED_VERTICALS = ["enthusiast_vertical"]`, plus agents, integrations, managers and entities). The server, frontend, LLM providers and core agent framework live in the Suvereo repository.

Enthusiast 1.7 was the last standalone release (tag `v1.7.1`). Its documentation is kept frozen in `docs-v1.7/`.

## Repository Structure

```
plugins/      # Independent Python packages, each with its own pyproject.toml
docs/         # Documentation site (Next.js + Nextra), served at /tools/enthusiast
docs-v1.7/    # Frozen Enthusiast 1.7 documentation, served at /tools/enthusiast/v1.7. Do not update.
```

## Packages (`plugins/`)

Layering, from the bottom up:
- **`enthusiast-vertical-common`**: e-commerce contracts — `ProductSourcePlugin`, `DocumentSourcePlugin`, `ECommerceIntegrationPlugin`, `ECommercePlatformConnector`, data structures (`ProductDetails`, `DocumentDetails`, `Address`, ...), evaluation helpers. No Django; depends only on `suvereo-common`.
- **`enthusiast-vertical`**: the Django app — `Product`/`Document` models and migrations, retrievers, sync managers, agent builder and injector.
- **`enthusiast-vertical-tools`**: agent tools shared by the pre-built agents.
- **`enthusiast-source-*`**: integrations (sample, medusa, shopify, shopware, solidus, woocommerce, wordpress, sanitycms). Depend only on `enthusiast-vertical-common`.
- **`enthusiast-agent-*`**: pre-built agents (product-search, user-manual-search, order-intake, catalog-enrichment, catalog-web-import, invoice-scanning). Build on `suvereo-common`, `suvereo-agent-tool-calling`, `suvereo-agent-tools`, `enthusiast-vertical` and `enthusiast-vertical-tools`.

Core contracts (`BaseAgent`, tools, registries, configuration) come from the `suvereo-*` packages, not from this repository.

## Common Commands

- **Lint**: `ruff check plugins` and `ruff format --check plugins` (config in root `pyproject.toml`: line-length 120, target Python 3.12, import sorting enabled)
- **Build a package**: `cd plugins/<package> && poetry build`
- **Docs**: `cd docs && pnpm install && pnpm build` (Node 20)

Packages are published to PyPI on merge to `main` when their `pyproject.toml` changes (`.github/workflows/publish-plugins.yml`). Publish order matters: `enthusiast-vertical-common` → `enthusiast-vertical` / `enthusiast-vertical-tools` → sources and agents.

## Running Locally

There is no server in this repository. To run the vertical, install the packages (editable) into a Suvereo development environment and register them in Suvereo's `settings_override.py`. See `docs/content/docs/getting-started/installation.md` for the settings to add.

## Coding Conventions

- **OOP-first**: Favor object-oriented design — use classes, inheritance, and polymorphism. The plugin system relies on subclassing contracts in `suvereo-common` and `enthusiast-vertical-common`.
- **Docstrings on public interfaces**: All public classes and methods must have clear docstrings describing their purpose, parameters, and return values.
- **Keep `enthusiast-vertical-common` free of Django** so source plugins stay lightweight.
