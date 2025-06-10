import requests

from enthusiast_common import ProductDetails, ProductSourcePlugin


class ShopwareProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        """
        Initialize the plugin with the parameters to access source.

        Args:
            data_set_id (int): identifier of a data set that products are assigned to.
            config (dict): Parameters such as shop url or access token to configure a plugin.
        """
        super().__init__(data_set_id, config)

        # Source specific parameters.
        self._base_url = config.get("base_url", "")
        self._currency_iso_code = config.get("currency_iso_code", "")
        self._client_id = config.get("client_id", "")
        self._api_key = config.get("api_key", "")

        self._access_token = None
        self._categories = None
        self._currency_id = None
        self._properties = None
        self._property_options = None

    def _get_product(self, product_details):
        """Translates product definition received from Shopware into Enthusiast product.

        Args:
            product_details: a product returned by Shopware API
        Returns:
            ProductDetails: product definition used by ECL to sync a product.
        """
        return ProductDetails(
            entry_id=product_details.get("id"),
            name=product_details.get("attributes", {}).get("name"),
            slug=product_details.get("attributes", {}).get("name").replace(" ", "-"),
            description=product_details.get("attributes", {}).get("description", "-"),
            sku=product_details.get("attributes", {}).get("productNumber"),
            price=self._product_price(product_details),
            properties=self._product_properties(product_details),
            categories=str(
                [
                    self._product_category(category_id)
                    for category_id in product_details.get("attributes", {}).get("categoryTree")
                ]
            ),
        )

    def _get_access_token(self):
        if self._access_token:
            return self._access_token
        body = {"grant_type": "client_credentials", "client_id": self._client_id, "client_secret": self._api_key}
        response = requests.post(f"{self._base_url}/api/oauth/token", body)
        if response.status_code != 200:
            raise Exception("Failed to acquire access token. Please verify the client ID and API key.")

        self._access_token = response.json().get("access_token")
        return self._access_token

    def _build_headers(self):
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    def _fetch_products(self):
        response = requests.get(f"{self._base_url}/api/product", headers=self._build_headers())
        if response.status_code != 200:
            raise Exception("Failed to fetch products")

        data = response.json().get("data", [])

        # filtering out product variants
        data = filter(
            lambda o: o.get("type") == "product"
            and o.get("attributes", {}).get("productNumber")
            and "." not in o.get("attributes", {}).get("productNumber"),
            data,
        )
        return list(data)

    def _fetch_categories(self):
        if self._categories:
            return self._categories

        response = requests.get(f"{self._base_url}/api/category", headers=self._build_headers())
        if response.status_code != 200:
            raise Exception("Failed to fetch categories")

        self._categories = {
            category_data.get("id"): category_data.get("attributes", {}).get("name")
            for category_data in response.json().get("data")
        }

        return self._categories

    def _fetch_currency_id(self):
        if self._currency_id:
            return self._currency_id

        response = requests.get(f"{self._base_url}/api/currency", headers=self._build_headers())
        if response.status_code != 200:
            raise Exception("Failed to fetch currency id")

        data = response.json().get("data", [])
        self._currency_id = next(
            (c.get("id") for c in data if c.get("attributes", {}).get("isoCode") == self._currency_iso_code), None
        )

        return self._currency_id

    def _fetch_properties(self):
        if self._properties:
            return self._properties

        response = requests.get(f"{self._base_url}/api/property-group", headers=self._build_headers())
        if response.status_code != 200:
            raise Exception("Failed to fetch properties")

        data = response.json().get("data", [])
        self._properties = {
            property_data.get("id"): property_data.get("attributes", {}).get("name") for property_data in data
        }

        return self._properties

    def _fetch_property_options(self):
        if self._property_options:
            return self._property_options

        response = requests.get(f"{self._base_url}/api/property-group-option", headers=self._build_headers())
        if response.status_code != 200:
            raise Exception("Failed to fetch property options")

        data = response.json().get("data", [])
        self._property_options = {
            property_option_data.get("id"): {
                "name": property_option_data.get("attributes", {}).get("name"),
                "property_id": property_option_data.get("attributes", {}).get("groupId"),
            }
            for property_option_data in data
        }

        return self._property_options

    def _product_category(self, category_id):
        return self._fetch_categories().get(category_id)

    def _product_price(self, product_details):
        price = next(
            (
                price.get("gross")
                for price in product_details.get("attributes", {}).get("price")
                if price.get("currencyId") == self._fetch_currency_id()
            ),
            None,
        )
        return float(price) if price else None

    def _product_properties(self, product_details):
        if not product_details.get("attributes", {}).get("propertyIds"):
            return "-"
        product_properties = {}

        for property_option_id in product_details.get("attributes", {}).get("propertyIds"):
            property_option = self._fetch_property_options().get(property_option_id)
            property_name = self._fetch_properties().get(property_option.get("property_id"))

            if property_name not in product_properties.keys():
                product_properties[property_name] = []
            product_properties[property_name].append(property_option.get("name"))

        return " | ".join(
            [
                f"{property_name} -> {str(property_options)}"
                for property_name, property_options in product_properties.items()
            ]
        )

    def fetch(self) -> list[ProductDetails]:
        """Fetch product list.

        Returns:
            list[ProductDetails]: A list of products.
        """
        products = []
        for product_details in self._fetch_products():
            products.append(self._get_product(product_details))

        return products
