from typing import Any, Optional

from enthusiast_common import ProductDetails, ProductSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field
import json

from .medusa_api_client import MedusaAPIClient


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

    @staticmethod
    def get_product(medusa_product: dict[str, Any]) -> ProductDetails:
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
            description=medusa_product.get("description") or "",
            sku=(medusa_product.get("variants") or [{}])[0].get("ean") or "",
            price=MedusaProductSource._extract_product_price(medusa_product),
            properties=MedusaProductSource._parse_properties(medusa_product.get("variants", [{}])[0].get('options', {})),
            categories=(medusa_product.get("collection") or {}).get("title", ""),
        )

        return product

    @staticmethod
    def _parse_properties(raw_properties: list[dict[str, str|dict]]) -> str:
        properties = { raw_property["option"]["title"]: raw_property["value"]  for raw_property in raw_properties}
        return json.dumps(properties)

    @staticmethod
    def _extract_product_price(medusa_product: dict[str, Any]) -> Optional[float]:
        if not medusa_product.get("variants"):
            return None

        prices = medusa_product.get("variants", [{}])[0].get("prices", [{}])

        if len(prices) == 0:
            return None

        return prices[0].get("amount")

    def fetch(self) -> list[ProductDetails]:
        """Fetch product list.

        Returns:
            list[ProductDetails]: A list of products.
        """

        products = []
        offset = 0  # Starting point for product list pagination.
        limit = 100  # Page size.

        client = self._build_api_client()
        while True:
            data = client.get("/admin/products?expand=categories", params={"limit": limit, "offset": offset})

            medusa_products = data.get("products", [])
            for medusa_product in medusa_products:
                products.append(self.get_product(medusa_product))
            if len(medusa_products) < limit:
                break

            offset += limit

        return products

    def _build_api_client(self) -> MedusaAPIClient:
        return MedusaAPIClient(self.CONFIGURATION_ARGS.base_url.rstrip("/"), self.CONFIGURATION_ARGS.api_key)
