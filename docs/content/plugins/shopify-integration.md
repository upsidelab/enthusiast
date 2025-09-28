---
sidebar_position: 1
---

# Shopify Integration

The Shopify plugin for Enthusiast enables you to automatically import product information from Shopify.

## Installing the Plugin


First, install the `enthusiast-source-shopify` package using pip:

```shell
pip install enthusiast-source-shopify
```

Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_PRODUCT_SOURCE_PLUGINS = {
    ...
    "Shopify": "enthusiast_source_shopify.ShopifyProductSource"
}
```

Save the changes and restart the web server and the worker.

## Obtaining an Access Token

Follow Shopify's [custom app creation guide](https://help.shopify.com/en/manual/apps/app-types/custom-apps#update-admin-api-scopes-for-a-custom-app) to create a custom app and obtain an API key. Ensure the app has admin access to read products and variants.

## Syncing Shopify Products to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu. Then, click on "Sources" next to the desired data set.
Add a source using “Shopify” as the plugin and provide a JSON configuration with the following attributes:
```json
{
  "shop_url": "https://STORE_NAME.myshopify.com",
  "access_token": "ACCESS_TOKEN"
}
```

Replace the placeholders with the values obtained earlier.

Save the configuration and start the sync process. The products should appear in the "Synchronize" section.
