from enthusiast_common import ProductDetails, ProductSourcePlugin
from woocommerce import API
from urllib.parse import urlparse
import logging
import os

logger = logging.getLogger(__name__)


class WoocommerceProductSource(ProductSourcePlugin):
    def __init__(self, data_set_id, config: dict):
        super().__init__(data_set_id, config)
        self._woocommerce_url = config.get("base_url")
        self._per_page = self._validate_per_page(config.get("per_page", 20))
        self._woocommerce_consumer_key, self._woocommerce_consumer_secret = self._get_credentials(config)
        self.wcapi = self._initialize_api()

    def _validate_per_page(self, per_page):
        return max(10, min(int(per_page), 100))

    def _get_credentials(self, config):
        if "WOO_CONSUMER_KEY" in os.environ and "WOO_CONSUMER_SECRET" in os.environ:
            return os.environ["WOO_CONSUMER_KEY"], os.environ["WOO_CONSUMER_SECRET"]
        elif "consumer_key" in config and "consumer_secret" in config:
            return config["consumer_key"], config["consumer_secret"]
        else:
            raise ValueError("WooCommerce consumer key and secret not provided")

    def _check_url_security(self):
        if not self._woocommerce_url:
            raise ValueError("WooCommerce URL is not set")

        parsed_url = urlparse(self._woocommerce_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid WooCommerce URL: {self._woocommerce_url}")

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
            url=self._woocommerce_url,
            consumer_key=self._woocommerce_consumer_key,
            consumer_secret=self._woocommerce_consumer_secret,
            version="wc/v3",
            timeout=30,
            verify_ssl=is_secure,
        )

    def fetch(self) -> list[ProductDetails]:
        results = []
        page = 1
        while True:
            try:
                response = self.wcapi.get("products", params={"page": page, "per_page": self._per_page})

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
