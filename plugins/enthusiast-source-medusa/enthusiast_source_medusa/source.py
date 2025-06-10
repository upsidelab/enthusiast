import requests

from enthusiast_common import ProductDetails, ProductSourcePlugin


class MedusaProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        """
        Initialize the plugin with the parameters to access source.

        Args:
            data_set_id (int): identifier of a data set that products are assigned to.
            config (dict): Parameters such as shop url or access token to configure a plugin.
        """
        super().__init__(data_set_id, config)

        # Source specific parameters.
        self._base_url = config.get("base_url")
        self._api_key = config.get("api_key")

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
            properties=medusa_product.get("metadata"),
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

        endpoint = f"{self._base_url}/admin/products?expand=categories"
        products = []
        offset = 0  # Starting point for product list pagination.
        limit = 100  # Page size.

        headers = {"Authorization": f"Bearer {self._api_key}"}

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
