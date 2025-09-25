import base64

import requests
from enthusiast_common import ProductDetails, ProductSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field


class MedusaProductSourceConfig(RequiredFieldsModel):
    api_key: str = Field(title="API key", description="Medusa API key")
    base_url: str = Field(title="Base url", description="Medusa API base url")


class MedusaProductSource(ProductSourcePlugin):
    CONFIGURATION_ARGS = MedusaProductSourceConfig

    def __init__(self, data_set_id):
        """
        Initialize the plugin with the parameters to access source.

        Args:
            data_set_id (int): identifier of a data set that products are assigned to.
        """
        super().__init__(data_set_id)

    def get_product(self, medusa_product) -> ProductDetails:
        """Translates product definition received from Medusa into Enthusiast product.

        Args:
            medusa_product: a product returned by Medusa API
        Returns:
            ProductDetails: product definition used by ECL to sync a product.
        """
        product = ProductDetails(
            entry_id=medusa_product.get("id"),
            name=medusa_product.get("title"),
            slug=medusa_product.get("handle"),
            description=medusa_product.get("description"),
            sku=medusa_product.get("variants", [{}])[0].get("sku") if medusa_product.get("variants") else None,
            price=medusa_product.get("variants", [{}])[0].get("prices", [{}])[0].get("amount")
            if medusa_product.get("variants")
            else None,
            properties=medusa_product.get("metadata", ""),
            categories=[category.get("name") for category in medusa_product.get("collection", {}).get("categories", [])]
            if medusa_product.get("collection")
            else [],
        )

        return product

    def fetch(self) -> list[ProductDetails]:
        """Fetch product list.

        Returns:
            list[ProductDetails]: A list of products.
        """

        endpoint = f"{self.CONFIGURATION_ARGS.base_url}/admin/products?expand=categories"
        products = []
        offset = 0  # Starting point for product list pagination.
        limit = 100  # Page size.
        encoded_api_key_bytes = base64.b64encode(self.CONFIGURATION_ARGS.api_key.encode("utf-8"))
        encoded_api_key = encoded_api_key_bytes.decode("utf-8")

        headers = {"Authorization": f"Basic {encoded_api_key}"}

        while True:
            response = requests.get(endpoint, headers=headers, params={"limit": limit, "offset": offset})

            if response.status_code == 404:
                raise Exception("The endpoint was not found. Please verify the URL.")
            elif response.status_code != 200:
                raise Exception(f"Failed to fetch products: {response.status_code} - {response.text}")

            data = response.json()
            medusa_products = data.get("products", [])
            for medusa_product in medusa_products:
                products.append(self.get_product(medusa_product))
            if len(medusa_products) < limit:
                break

            offset += limit

        return products
