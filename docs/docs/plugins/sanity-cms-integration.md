---
sidebar_position: 3
---

# Sanity CMS Integration

The Sanity CMS plugin for Enthusiast enables you to automatically import documents from [Sanity CMS](https://www.sanity.io/).

## Installing the Plugin


First, install the `enthusiast-source-sanitycms` package using pip:

```shell
pip install enthusiast-source-sanitycms
```

Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_DOCUMENT_SOURCE_PLUGINS = {
    ...
    "Sanity": "enthusiast_source_sanitycms.SanityCMSDocumentSource"
}
```

Save the changes and restart the web server and the worker.

## Syncing Sanity CMS Content to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu. Then, click on "Sources" next to the desired data set.
Add a source using “Sanity” as the plugin and provide a JSON configuration with the following attributes:
```json
{
  "api_key": "<api key>",
  "project_id": "<project id in sanity>",
  "dataset": "<data set id in sanity>",
  "schema_type": "<type of documents to sync>",
  "title_field_name": "<the field to use as a title for synced documents>",
  "content_field_name": "<the field to use as content for synced documents>"
}
```

Save the configuration and start the sync process. The documents should appear in the "Synchronize" section.
