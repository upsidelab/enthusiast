---
sidebar_position: 2
---

# Using the Suvereo Starter

Enthusiast is installed into a Suvereo deployment, so you start from the [suvereo-starter](https://github.com/upsidelab/suvereo-starter) repository. It contains Dockerfiles and configuration that build your own deployment of Suvereo, including your custom code and the packages you install from PyPI, such as Enthusiast.

Clone it and create the env files:

```shell
$ git clone https://github.com/upsidelab/suvereo-starter
$ cd suvereo-starter
$ cp server/config/sample.env server/config/.env
$ cp frontend/config/sample.env frontend/config/.env
```

Set your API keys (for example `OPENAI_API_KEY`) in `server/config/.env`.

The repository uses the following structure:
```
server/
  config/
    .env <- Environment variables injected into the server.
    settings_override.py <- Your Suvereo configuration: domain definitions, agents, integrations.
  src/
    pyproject.toml <- Describes your code as a Python package. Add Enthusiast packages as dependencies here.
    ... <- Your own agents, integrations and other code.
  Dockerfile <- Builds the server image with your code and its dependencies installed.
frontend/
  config/
    .env <- Environment variables for the frontend.
```

## Adding Enthusiast

Add the Enthusiast packages you need to the dependencies of your package in `server/src/`, for example:

```shell
$ cd server/src
$ poetry add enthusiast-vertical enthusiast-source-sample enthusiast-agent-product-search
```

They are installed into the server image together with your code.

Then register the domain definition and its plugins in `server/config/settings_override.py`, as described in the [installation guide](/docs/getting-started/installation#configuring-suvereo).

## Running It

Build and start the stack with Docker Compose:

```shell
$ docker compose build && docker compose up
```

The admin UI is available at http://localhost:10001 and the API at http://localhost:10000. The domain definition's migrations are applied when the server starts.

To write your own e-commerce agents in `server/src/`, see [E-commerce Agents](/docs/agents/agent-types) and [Concept: Product Search Agent](/docs/customization/concept-product-search).
