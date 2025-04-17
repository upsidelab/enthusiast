---
sidebar_position: 6
---

# Create a Custom Plugin

## Create a Custom Product or Document Source

To integrate Enthusiast with an unsupported e-commerce or CMS system, create a custom plugin. You can also customize an existing plugin to change its data mapping. Enthusiast provides interfaces for plugins to supply data to the system.

The recommended approach is to create a new Python library and install it in your environment.

We suggest using Poetry for package creation:

```shell
poetry new my-custom-source-plugin
cd my-custom-source-plugin
```

Add `enthusiast-common` as a dependency, access the required interfaces:

```shell
poetry add enthusiast-common
```

Next, implement your custom source. Create a file named `source.py` and define a plugin class that implements the `ProductSourcePlugin` interface:
```python title="my-custom-source-plugin/my_custom_source_plugin/source.py"
from enthusiast_common import ProductDetails, ProductSourcePlugin

class MyCustomProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id: int, config: dict):
        super().__init__(data_set_id, config)
        # Add your custom initialization here
        
    def fetch(self) -> list[ProductDetails]:
        results = []
        # Add your integration here and fill the results
        # list with Product Details objects 
        # results.append(
        #   ProductDetails(entry_id="", 
        #                  name="", 
        #                  slug="", 
        #                  sku="", 
        #                  description="", 
        #                  properties="", 
        #                  categories="", 
        #                  price="")
        # )
        
        return results
```

For a document source plugin, use a similar approach: 
```python title="my-custom-source-plugin/my_custom_source_plugin/source.py
from enthusiast_common import DocumentDetails, DocumentSourcePlugin

class MyCustomDocumentSource(DocumentSourcePlugin):
    def __init__(self, data_set_id: int, config: dict):
        super().__init__(data_set_id, config)
        # Add your custom initialization here

    def fetch(self) -> list[DocumentDetails]:
        results = []
        # Add your integration here and fill the result 
        # list with Document Details objects 
        # results.append(
        #   DocumentDetails(url="",
        #                   title="",
        #                   content="")
        # )

        return results
```

Export the plugin classes in the `__init__.py` file
```python title="my-custom-source-plugin/my_custom_source_plugin/__init__.py
from .source import MyCustomProductSource as MyCustomProductSource
from .source import MyCustomDocumentSource as MyCustomDocumentSource
```

Finally, install the package in your environment, and configure the plugin in Enthusiast's `settings.py`:

```python title=server/pecl/settings.py
CATALOG_DOCUMENT_SOURCE_PLUGINS = {
    ...
    "My Source": "my_custom_source_plugin.MyCustomDocumentSource"
}

...

CATALOG_PRODUCT_SOURCE_PLUGINS = {
    ...
    "My Source": "my_custom_source_plugin.MyCustomProductSource"
}
```

Restart the server to enable the plugin. Then, use the UI to create a new data source that uses the plugin.

## Further reading

- [Interface definitions in the enthusiast-common package](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py)
- [Sample product source implementation](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-source-sample/enthusiast_source_sample/product_source.py)
- [Sample document source implementation](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-source-sample/enthusiast_source_sample/document_source.py)