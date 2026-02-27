# Building a Custom Integration

Custom integrations let you connect Enthusiast to systems that aren’t supported out of the box.

## Types of Integrations.

1. E-Commerce Integration - Enables bidirectional communication between agents and an e-commerce system.
2. Product Source Integration - Enables one-way fetching of product data from an e-commerce or PIM system.
3. Document Source Integration - Enables one-way fetching of documents such as manuals, FAQs, or internal content.
4. Language Model Integration - Connects agents to a language model provider.

## Building an E-Commerce Integration

An E-Commerce Integration enables bidirectional communication between Enthusiast AI Agents and an e-commerce platform.

To build one, implement the [enthusiast_common.interfaces.ECommerceIntegrationPlugin](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py#L69) interface.

Your integration class must define two static fields:
- `NAME` - The name shown to admins in the integrations list.
- `CONFIGURATION_ARGS` - A subclass of [enthusiast_common.utils.RequiredFieldsModel](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/utils.py#L77) defining the integration's configuration schema.

Your class must also implement the following methods:
- `build_connector(self)` - Returns an implementation of [enthusiast_common.connector.ECommercePlatformConnector](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/connectors/ecommerce_platform_connector.py). This connector is available to agents at runtime.
- `build_product_source(self)` - Returns an implementation of [enthusiast_common.interfaces.ProductSourcePlugin](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py#L36), used to build a local product index.

### Example Implementation

```python
class UpCommerceIntegrationConfig(RequiredFieldsModel):
    base_url: str = Field(description="Base URL for the API")
    api_key: str = Field(description="API key for connecting to the E-Commerce platform")
    
class UpCommerceIntegration(ECommerceIntegrationPlugin):
    NAME = "UpCommerce"
    CONFIGURATION_ARGS = UpCommerceIntegrationConfig
    
    def build_connector(self) -> ECommercePlatformConnector:
        return UpCommercePlatformConnector(base_url=self.CONFIGURATION_ARGS.base_url,
                                           api_key=self.CONFIGURATION_ARGS.api_key)
                                           
   def build_product_source(self) -> ProductSourcePlugin:
        return UpCommerceProductSource(base_url=self.CONFIGURATION_ARGS.base_url,
                                       api_key=self.CONFIGURATION_ARGS.api_key)
                                       
class UpCommercePlatformConnector(ECommercePlatformConnector):
    def create_empty_order(self, email: Optional[str] = None, address: Optional[Address] = None) -> str:
        ...

    def add_to_order(self, order_id: str, sku: str, quantity: int) -> bool:
        ...

    def create_order_with_items(self, items: list[tuple[str, int]], email: Optional[str] = None, address: Optional[Address] = None) -> str:
        ...

    def get_product_by_sku(self, sku: str) -> ProductDetails:
        ...

    def create_product(self, product_details: ProductDetails) -> str:
        ...

    def update_product(self, sku: str, product_details: ProductDetails) -> bool:
        ...

    def get_admin_url_for_order_id(self, order_id: str) -> str:
        ...
    
class UpCommerceProductSource(ProductSourcePlugin):
    def fetch(self) -> list[ProductDetails]:
        return [ProductDetails( ... )]
```

## Building a Product Source Integration

A Product Source enables one-way fetching of product data from an e-commerce or PIM system. 

To build a product source, implement the [enthusiast_common.interfaces.ProductSourcePlugin](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py#L36) interface.

Your integration class must define the following static field:
- `CONFIGURATION_ARGS` - A subclass of [enthusiast_common.utils.RequiredFieldsModel](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/utils.py#L77) defining the integration's configuration schema.

It should also implement the following method:
- `fetch(self)` - Returns a list of [enthusiast_common.structures.ProductDetails](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/structures.py#L19). These products will be indexed in Enthusiast.

### Example Implementation

```python
class UpCommerceProductSource(ProductSourcePlugin):
    def fetch(self) -> list[ProductDetails]:
        return [ProductDetails( ... )]
```

## Building a Document Source Integration

A Document Source enables one-way fetching of documents such as manuals, FAQs, or internal content.

To build a document source, implement the [enthusiast_common.interfaces.DocumentSourcePlugin](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/interfaces.py#L52) interface.

Your integration class must define the following static field:
- `CONFIGURATION_ARGS` - A subclass of [enthusiast_common.utils.RequiredFieldsModel](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/utils.py#L77) defining the integration's configuration schema.

It should also implement the following method:
- `fetch(self)` - Returns a list of [enthusiast_common.structures.DocumentDetails](https://github.com/upsidelab/enthusiast/blob/main/plugins/enthusiast-common/enthusiast_common/structures.py#L31). These documents will be indexed in Enthusiast.

### Example Implementation

```python
class UpCommerceDocumentSource(DocumentSourcePlugin):
    def fetch(self) -> list[DocumentDetails]:
        return [DocumentDetails( ... )]
```
