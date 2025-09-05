import requests
from enthusiast_common import ProductDetails, ProductSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field


class SolidusConfig(RequiredFieldsModel):
    base_url: str = Field(description="Solidus API base URL")
    api_key: str = Field(description="Solidus API key")


class SolidusProductSource(ProductSourcePlugin):
    CONFIGURATION_ARGS = SolidusConfig

    def __init__(self, data_set_id, **kwargs):
        super().__init__(data_set_id)

    @staticmethod
    def get_properties(solidus_properties):
        properties = [f"{item['property_name']} -> {item['value']}" for item in solidus_properties]
        return "|".join(properties)

    def get_product(self, solidus_product) -> ProductDetails:
        """Translates product definition received from Solidus into Enthusiast product.

        Args:
            solidus_product: a product returned by Solidus API
        Returns:
            ProductDetails: product definition used by ECL to sync a product.
        """
        product = ProductDetails(
            entry_id=solidus_product.get("id"),
            name=solidus_product.get("name"),
            slug=solidus_product.get("slug"),
            description=solidus_product.get("description") or "-",
            sku=solidus_product.get("master", [{}]).get("sku") if solidus_product.get("master") else None,
            price=float(solidus_product.get("price")),
            properties=self.get_properties(solidus_product.get("product_properties")),
            categories=str(
                [taxon.get("name") for taxon in solidus_product.get("classifications", {}).get("taxon", [])]
                if solidus_product.get("collection")
                else []
            ),
        )

        return product

    def fetch(self) -> list[ProductDetails]:
        """Fetch product list.

        Returns:
            list[ProductDetails]: A list of products.
        """

        endpoint = f"{self.CONFIGURATION_ARGS.base_url}/api/products"

        products = []
        page = 1
        headers = {"Authorization": f"Bearer {self.CONFIGURATION_ARGS.api_key}"}

        while True:
            response = requests.get(endpoint, headers=headers, params={"page": page})

            if response.status_code == 404:
                raise Exception("The endpoint was not found. Please verify the URL.")
            elif response.status_code != 200:
                raise Exception(f"Failed to fetch products: {response.status_code} - {response.text}")

            data = response.json()
            solidus_products = data.get("products", [])
            for solidus_product in solidus_products:
                products.append(self.get_product(solidus_product))
            if page >= data["pages"]:
                break

            page += 1

        return products
