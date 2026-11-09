---
sidebar_position: 2
---

# Using the Suvereo Starter

Enthusiast is installed into a Suvereo deployment built from the [suvereo-starter](https://github.com/upsidelab/suvereo-starter) repository. It contains Dockerfiles and configuration that build your own deployment of Suvereo, including your custom code and the packages you install from PyPI, such as Enthusiast. To set it up with Enthusiast, follow the [installation guide](/docs/getting-started/installation).

This page describes where your own code and configuration go.

## Repository Structure

```
server/
  config/
    .env <- Environment variables injected into the server.
    settings_override.py <- Your Suvereo configuration: verticals, agents, integrations.
  src/
    pyproject.toml <- Describes your code as a Python package. Enthusiast packages are its dependencies.
    ... <- Your own agents, integrations and other code.
  Dockerfile <- Builds the server image with your code and its dependencies installed.
frontend/
  config/
    .env <- Environment variables for the frontend.
```

The server image is built from `server/src/` and `server/config/settings_override.py`. After changing either of them, rebuild the image and restart the containers:

```shell
docker compose build && docker compose up
```

## Adding Your Own Code

Put your own agents, integrations and tools in the package in `server/src/`, next to the Enthusiast packages it depends on. Register them in `server/config/settings_override.py` the same way as the pre-built ones, using your package's module path:

```python
AVAILABLE_AGENTS = [
    "enthusiast_agent_product_search.ProductSearchAgent",
    "my_package.agents.MyAgent",
]
```

To write your own e-commerce agents, see [E-commerce Agents](/docs/agents/agent-types) and [Concept: Product Search Agent](/docs/customization/concept-product-search).
