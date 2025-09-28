---
sidebar_position: 5
---

# WordPress Integration

The WordPress plugin for Enthusiast enables you to automatically import blog posts from WordPress.

## Installing the Plugin


First, install the `enthusiast-source-wordpress` package using pip:

```shell
pip install enthusiast-source-wordpress
```

Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_DOCUMENT_SOURCE_PLUGINS = {
    ...
    "Wordpress": "enthusiast_source_wordpress.WordpressDocumentSource"
}
```

Save the changes and restart the web server and the worker.

## Syncing WordPress Posts to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu. Them. click on "Sources" next to the desired data set.
Add a source using “Wordpress” as the plugin and provide a JSON configuration with the following attributes:
```json
{
  "base_url": "BASE_URL",
  "user_agent": "USER_AGENT"
}
```

Replace BASE_URL with the root of the WordPress site that you'd like to import (e.g. https://example.com).
The `user_agent` attribute is optional, and can be omitted.

Save the configuration and start the sync process. The documents should appear in the "Synchronize" section.
