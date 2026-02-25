import logging
from urllib.parse import urlparse

from enthusiast_common import ProductDetails, ProductSourcePlugin
from enthusiast_common.utils import RequiredFieldsModel
from pydantic import Field
from woocommerce import API

logger = logging.getLogger(__name__)


class WoocommerceConfig(RequiredFieldsModel):
    base_url: str = Field(title="Base URL", description="WooCommerce site base URL")
    per_page: int = Field(title="Products per page", default=20, description="Number of products per page (10-100)")
    consumer_key: str = Field(title="Consumer key", description="WooCommerce consumer key")
    consumer_secret: str = Field(title="Consumer secret", description="WooCommerce consumer secret")


class WoocommerceProductSource(ProductSourcePlugin):
    NAME = "WooCommerce"
    CONFIGURATION_ARGS = WoocommerceConfig

    def __init__(self, data_set_id, **kwargs):
        super().__init__(data_set_id)

    def _validate_per_page(self, per_page):
        return max(10, min(int(per_page), 100))

    def _check_url_security(self):
        if not self.CONFIGURATION_ARGS.base_url:
            raise ValueError("WooCommerce URL is not set")

        parsed_url = urlparse(self.CONFIGURATION_ARGS.base_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid WooCommerce URL: {self.CONFIGURATION_ARGS.base_url}")

        scheme = parsed_url.scheme.lower()
        match scheme:
            case "https":
                return True
            case "http":
                logger.warning(
                    "HTTP protocol detected for WooCommerce URL. This is not recommended for production environments due to security risks. Please consider using HTTPS."
                )
                return False
            case _:
                raise ValueError(f"Unsupported protocol in WooCommerce URL: {scheme}")

    def _initialize_api(self):
        is_secure = self._check_url_security()
        return API(
            url=self.CONFIGURATION_ARGS.base_url,
            consumer_key=self.CONFIGURATION_ARGS.consumer_key,
            consumer_secret=self.CONFIGURATION_ARGS.consumer_secret,
            version="wc/v3",
            timeout=30,
            verify_ssl=is_secure,
        )

    def fetch(self) -> list[ProductDetails]:
        wcapi = self._initialize_api()
        results = []
        page = 1
        while True:
            try:
                response = wcapi.get(
                    "products",
                    params={"page": page, "per_page": self._validate_per_page(self.CONFIGURATION_ARGS.per_page)},
                )

                if response.status_code != 200:
                    logger.error(f"Failed to fetch products. Status code: {response.status_code}")
                    break

                products = response.json()

                if not products:
                    break

                for product in products:
                    results.append(self._convert_to_product_details(product))

                page += 1
            except Exception as e:
                logger.error(f"Error fetching products: {str(e)}")
                break

        return results

    def _convert_to_product_details(self, woo_product: dict) -> ProductDetails:
        return ProductDetails(
            entry_id=str(woo_product["id"]),
            name=woo_product["name"],
            slug=woo_product["slug"],
            description=woo_product["description"],
            sku=woo_product["sku"],
            properties=str(
                {
                    "status": woo_product["status"],
                    "featured": woo_product["featured"],
                    "catalog_visibility": woo_product["catalog_visibility"],
                    "type": woo_product["type"],
                }
            ),
            categories=", ".join(category["name"] for category in woo_product["categories"]),
            price=float(woo_product["price"]) if woo_product["price"] else 0.0,
        )
