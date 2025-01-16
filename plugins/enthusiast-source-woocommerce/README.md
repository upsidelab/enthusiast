# WooCommerce Integration

## This Enthusiast plugin enables the import of product data directly from WooCommerce.

### First, install the `enthusiast-source-woocommerce` package using pip:

```shell
pip install enthusiast-source-woocommerce
```


### Then, enable the plugin by adding it to the `settings.py`:

```python title="server/pecl/settings.py"
CATALOG_PRODUCT_SOURCE_PLUGINS = {
    ...
    "WooCommerce": "enthusiast_source_woocommerce.WoocommerceProductSource"
}
```

### Set WooCommerce consumer key and secret by setting enviroment variables

```
WOO_CONSUMER_KEY=consumerkey
WOO_CONSUMER_SECRET=consumersecret
```

#### OR continue reading to implement Consumer Key and Secret instead in sources configuration.

Save the changes and restart the web server and the worker.

## Syncing WooCommerce Products to a Data Set

Log in as an admin user and go to Manage → Data Sets from the left-hand menu.

Then. click on "Sources" next to the desired data set.

Add a source using “WooCommerce” as the plugin and provide a JSON configuration with the following attributes:

### Provide base url to your shop.

```json
{
  "base_url": "BASE_URL",
}
```

### If you decide to add Consumer Key and Secrect directly to sources

```json
{
    ...
  "consumer_key": "consumerkey",
  "consumer_secret": "consumersecret"
}
```

### By default synchronization will obtain 20 products per page.

You can change this by setting up "per_page" in your config.

`Min. 10, max 100`

```json
{
    ...
  "per_page": 10
}
```

## Example configuration for source

```json
{
    "base_url": "http://localhost:8080",
    "consumer_key": "mykey",
    "consumer_secret": "mysecret",
    "per_page": 10
}
```