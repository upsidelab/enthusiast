import json
import shopify

from enthusiast_common import ProductDetails, ProductSourcePlugin


class ShopifyProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        """
        Initialize the plugin with the parameters to access shop.

        Args:
            data_set_id (int): identifier of a data set that products are assigned to.
            config (dict): Parameters such as shop url or access token to configure a plugin.
        """
        super().__init__(data_set_id, config)

        self.shop_url = config.get("shop_url")
        self.access_token = config.get("access_token")
        self.session = shopify.Session(self.shop_url, "2024-10", self.access_token)
        shopify.ShopifyResource.activate_session(self.session)

    def get_query_template(self):
        """Prepares template for querying shopify platform.

        Template is used to run queries to loop through all pages returned by Shopify.
        """

        return """query ($first: Int!, $after: String) {
            products(first: $first, after: $after) {
                edges {
                    node {
                        id
                        title
                        description
                        productType
                        tags
                        handle
                        productType
                        category {fullName}
                        variants(first: 50) {
                            edges {
                                node {
                                    title
                                    price
                                    sku
                                }
                            }
                        }
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
    """

    def get_product(self, shopify_product) -> ProductDetails:
        """Translates product definition received from Shopify into ECL product.

        Args:
            shopify_product: a product returned by Shopify API
        Returns:
            ProductDetails: product definition used by ECL to sync a product.
        """

        product = ProductDetails(
            entry_id=shopify_product["id"],
            name=shopify_product["title"],
            slug=shopify_product["handle"],
            description=shopify_product["description"],
            # SKUs and prices are defined at a variant's level.
            sku="",
            price=0,
            # Combine several attributes to create meaningful properties.
            properties=str(
                {
                    "productType": shopify_product.get("productType", ""),
                    "tags": shopify_product.get("tags", ""),
                }
            ),
            categories=shopify_product.get("category", "")
        )
        # Collect attributes from variants level.
        prices = []
        skus = []
        for variant_edge in shopify_product.get("variants", {}).get("edges", []):
            prices.append(float(variant_edge["node"].get("price", 0)))
            skus.append(str(variant_edge["node"].get("sku", "")))

        product.price = min(prices)
        product.sku = ", ".join(skus)

        return product

    def fetch(self) -> list[ProductDetails]:
        """Fetch product list.

        Returns:
            list[ProductDetails]: A list of products.
        """

        query = self.get_query_template()
        products = []
        has_next_page = True
        cursor = None

        while has_next_page:
            variables = {
                "first": 50,
                 "after": cursor
            }

            response = shopify.GraphQL().execute(query, variables=variables)

            result_data = json.loads(response)
            products_data = result_data.get("data", {}).get("products", {})
            product_edges = products_data.get("edges", [])
            page_info = products_data.get("pageInfo", {})

            for product_edge in product_edges:
                products.append(self.get_product(product_edge["node"]))

            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")

        return products
