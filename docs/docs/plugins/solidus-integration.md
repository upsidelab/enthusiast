---
sidebar_position: 3
---

# Solidus Integration

The Solidus plugin for Enthusiast enables you to automatically import product information from [Solidus](https://solidus.io).

## Installing the Plugin


First, install the `enthusiast-source-solidus` package using pip:

```shell
pip install enthusiast-source-solidus
```

Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_PRODUCT_SOURCE_PLUGINS = {
    ...
    "Solidus": "enthusiast_source_solidus.SolidusProductSource"
}
```

Save the changes and restart the web server and the worker.

## Obtaining an Access Token

Follow Solidus's [guide for accessing the API](https://solidus.stoplight.io/#api-key) to an API key.

## Syncing Solidus Products to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu. Then, click on "Sources" next to the desired data set.
Add a source using “Solidus” as the plugin and provide a JSON configuration with the following attributes:
```json
{
  "base_url": "<the root url to your Solidus store>",
  "api_key": "<api key>"
}
```

Replace the placeholders with the values obtained earlier.

Save the configuration and start the sync process. The products should appear in the "Synchronize" section.
