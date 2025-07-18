---
sidebar_position: 2
---

# Using Enthusiast Starter


The [enthusiast-starter](https://github.com/upsidelab/enthusiast-starter/) repository contains a set of Dockerfiles and scripts that make it easy to build your own deployment, including your custom agents and plugins.

Simply clone it and fill the config/env file to get started:

```shell
$ git clone https://github.com/upsidelab/enthusiast-starter
$ cp config/env.sample config/env
```

This will give you a local environment for building your custom code.

The repository uses the following structure:
```
config/
  env <- Environment variables to be injected into the server deployment.
  settings_override.py <- The overrides to Enthusiast's configuration, that supersede the default configuration.
src/
  pyproject.toml <- A poetry configuration file for your own enthusiast-custom package. You can add additional Enthusiast plugins as dependencies here, as well as third-party libraries required by your custom code.
  enthusiast_custom/ <- Your custom code goes here.
    examples/ <- Example agent and plugin implementations. You can remove it.
Dockerfile <- A Dockerfile for the server component, that bundles your custom code and installs it inside Enthusiast.
Dockerfile.development <- The same as above, except it runs the server in development mode.
```

You can then run an instance using docker compose:

```shell
$ docker compose build && docker compose up
```
