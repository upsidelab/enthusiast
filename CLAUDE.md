# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enthusiast is an open-source Agentic AI Framework for E-commerce. It provides RAG, vector search, and workflow orchestration for building AI-powered agents (product search, catalog enrichment, OCR-to-order, user manual search). Full-stack: Django backend + React frontend with a plugin architecture for agents, LLM providers, and data sources.

## Repository Structure

```
frontend/          # React 18 + TypeScript + Vite
server/            # Django 5 + DRF + Celery
plugins/           # Independent Python packages (agents, models, sources)
docker-compose.yml # Production deployment
docker-compose.development.yml
```

## Common Commands

### Frontend (`cd frontend`)
- **Install**: `pnpm install`
- **Dev server**: `pnpm run dev` (requires `VITE_API_BASE` and `VITE_WS_BASE` env vars)
- **Build**: `pnpm build` (runs `tsc -b && vite build`)
- **Lint**: `pnpm run lint`
- **Lint fix**: `pnpm run lint:fix`

### Backend (`cd server`)
- **Install**: `poetry install`
- **Run server**: `./manage.py runserver`
- **Run Celery worker**: `celery -A pecl.celery worker`
- **Run Celery beat**: `celery -A pecl.celery beat`
- **Migrations**: `./manage.py migrate`
- **Run all tests**: `pytest`
- **Run single test file**: `pytest agent/tests/test_views.py`
- **Run single test**: `pytest agent/tests/test_views.py::TestClassName::test_method`

### Linting (Python)
- **Ruff** is the Python linter. Config in root `pyproject.toml`: line-length 120, target Python 3.12, import sorting enabled.
- First-party packages: `agent`, `account`, `catalog`, `pecl`, `sync`

### Docker
- **Dev**: `docker compose -f docker-compose.development.yml up`
- **Prod**: `docker compose up`
- Services: postgres (pgvector), redis, api, frontend, worker, beat

## Architecture

### Backend (Django)

Four Django apps under `server/`:
- **agent** — Agent orchestration, conversations, messages, WebSocket consumers, file upload/parsing
- **catalog** — DataSets, Products, Documents, ProductContentChunks/DocumentChunks (pgvector embeddings), source configs, e-commerce integrations
- **account** — User model, auth (DRF token auth), user management
- **sync** — Source synchronization engine for products and documents (abstract base syncer pattern)

**Key backend patterns:**
- **Agent execution engine** (`agent/core/`): `AgentBuilder` instantiates agents, registries discover available agent types and LLM providers dynamically from plugins
- **Conversation flow**: `ConversationManager` (`agent/conversation/manager.py`) orchestrates conversations. Memory strategies: persistent, limited, summary (`agent/core/memory/`)
- **Vector embeddings**: Products → `ProductContentChunk`, Documents → `DocumentChunk` stored via pgvector in PostgreSQL
- **Background tasks**: Celery handles file processing, sync operations, scheduled cleanup. Redis as broker
- **Real-time**: Django Channels + Daphne for WebSocket streaming of agent responses
- **API docs**: Swagger at `/api/docs/` via drf-yasg

**URL routing**: All apps mount at root in `pecl/urls.py` via `include()`. API endpoints prefixed with `/api/`.

**Settings**: `pecl/settings.py` with `pecl/settings_override.py` for env-based overrides. Plugin lists (agents, models, sources, parsers) are configured in settings.

### Frontend (React + TypeScript)

- **Entry**: `src/main.tsx` defines routes via React Router DOM `createBrowserRouter`
- **Layout**: `src/App.tsx` wraps all authenticated routes with `ApplicationContextProvider` and sidebar
- **State**: React Context API via `ApplicationContext` — holds dataSets, current dataSetId, availableAgents, account info
- **API client**: `src/lib/api.ts` — `ApiClient` class with modular sub-clients (`conversations()`, `dataSets()`, `agents()`, `catalog()`, `users()`, `config()`)
- **Auth**: Token-based via `AuthenticationProvider`. `protectedLoginLoader` redirects unauthenticated users
- **UI components**: `src/components/ui/` contains Radix UI primitives styled with Tailwind (excluded from ESLint)
- **Forms**: React Hook Form + Zod for validation
- **Path alias**: `@/*` maps to `src/*`

### Plugin System

Plugins are standalone Python packages in `plugins/`:
- **Agent plugins** (`enthusiast-agent-*`): product-search, catalog-enrichment, ocr-to-order, user-manual-search, tool-calling, react
- **Model plugins** (`enthusiast-model-*`): openai, azureopenai, google, mistral, ollama
- **Source plugins** (`enthusiast-source-*`): sample, medusa, shopify, shopware, solidus, woocommerce, wordpress, sanitycms
- **Shared**: `enthusiast-common`, `enthusiast-file-parsers`

**`enthusiast-common`** is the core interfaces package that all plugins depend on. It defines the abstract base classes and contracts that the plugin system is built around:
- **Plugin interfaces**: `ProductSourcePlugin`, `DocumentSourcePlugin`, `ECommerceIntegrationPlugin` — ABCs that source plugins implement
- **Agent framework**: `BaseAgent` (with `get_answer()`), `BaseAgentBuilder` (factory), agent type enum (BASE, RE_ACT, TOOL_CALLING)
- **Registry bases**: `BaseAgentRegistry`, `BaseLanguageModelRegistry`, `BaseEmbeddingProviderRegistry` — for dynamic plugin discovery
- **Repository pattern**: Generic `BaseRepository[T]` and specialized bases (`BaseProductRepository`, `BaseConversationRepository`, etc.) for data access
- **Retriever bases**: `BaseRetriever`, `BaseProductRetriever`, `BaseVectorStoreRetriever` — for RAG/vector search
- **Tool system**: `BaseTool`, `BaseFunctionTool`, `BaseLLMTool`, `BaseAgentTool` — for building agent capabilities
- **E-commerce connector**: `ECommercePlatformConnector` ABC for order/product management across platforms
- **Data structures**: `ProductDetails`, `DocumentDetails`, `Address`, `LLMFile`, content types
- **Configuration**: Pydantic config models (`AgentConfig`, `LLMConfig`, `RepositoriesConfig`) and prompt template system (`ChatPromptTemplateConfig`, `MessageRole`)
- **Dependency injection**: `BaseInjector` provides retrievers, connectors, and memory to agents

Each plugin has its own `pyproject.toml` and is installed via poetry.

## Coding Conventions

- **OOP-first**: Favor object-oriented design — use classes, inheritance, and polymorphism. The codebase is built around abstract base classes and the plugin system relies on subclassing contracts in `enthusiast-common`.
- **Docstrings on public interfaces**: All public classes and methods must have clear docstrings describing their purpose, parameters, and return values.

## Test Patterns (Backend)

- Framework: pytest-django with model-bakery for test data
- Global fixtures in `server/conftest.py`: `user`, `admin_user`, `api_client` (authenticated), `admin_api_client`, `data_set`, `conversation`, `temp_media_root`
- Test locations: `agent/tests/`, `catalog/tests/`, `agent/core/memory/tests/`, `utils/tests/`
- Settings module: `DJANGO_SETTINGS_MODULE = pecl.settings` (in `pytest.ini`)

## Key Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | Django 5.2, DRF 3.16 |
| Task queue | Celery 5.5 + Redis |
| WebSocket | Django Channels + Daphne |
| Vector DB | PostgreSQL + pgvector |
| LLM framework | LangChain 0.3 |
| Frontend framework | React 18 + TypeScript 5.8 |
| Build tool | Vite 5.4 |
| Styling | Tailwind CSS 3.4 |
| Package managers | pnpm (frontend), poetry (backend) |
