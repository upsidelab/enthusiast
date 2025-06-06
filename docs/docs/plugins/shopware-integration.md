---
sidebar_position: 2
---

# Shopware Integration

The Shopware plugin for Enthusiast enables you to automatically import product information from [Shopware](https://www.shopware.com).

## Installing the Plugin


First, install the `enthusiast-source-shopware` package using pip:

```shell
pip install enthusiast-source-shopware
```

Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_PRODUCT_SOURCE_PLUGINS = {
    ...
    "Shopware": "enthusiast_source_shopware.ShopwareProductSource"
}
```

Save the changes and restart the web server and the worker.

## Obtaining Credentials

Follow Shopwware's guide for [creating an integration](https://docs.shopware.com/en/shopware-6-en/settings/system/integrationen). 

## Syncing Shopware Products to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu. Then, click on "Sources" next to the desired data set.
Add a source using "Shopware" as the plugin and provide a JSON configuration with the following attributes:
```json
{
  "base_url": "https://mystore.com",
  "client_id": "CLIENT_ID",
  "access_token": "ACCESS_TOKEN",
  "currency_iso_code": "EUR"
}
```

Replace the placeholders for `CLIENT_ID` and `ACCESS_TOKEN` with the values obtained when creating an integration.

Save the configuration and start the sync process. The products should appear in the "Synchronize" section.
