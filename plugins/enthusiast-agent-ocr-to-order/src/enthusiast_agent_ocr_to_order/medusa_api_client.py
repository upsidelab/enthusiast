import base64
import logging
import os

import requests

logger = logging.getLogger(__name__)


class MedusaAPIClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.environ.get("MEDUSA_BASE_URL")
        self.api_key = api_key or os.environ.get("MEDUSA_API_KEY")

    def _get_headers(self):
        encoded_api_key_bytes = base64.b64encode(os.environ.get("MEDUSA_API_KEY").encode("utf-8"))
        encoded_api_key = encoded_api_key_bytes.decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_api_key}",
        }

    def get_variants(self, product_id: str):
        """
        Fetch all variants for a given product.
        """
        try:
            url = f"{self.base_url}/admin/products/{product_id}"
            response = requests.get(url, headers=self._get_headers())
            return response.json()
        except Exception as e:
            logger.error(e)

    def create_admin_order(self, customer_email: str, variant_ids: list[str], quantities: list[str]) -> dict:
        """
        Create an admin draft order.
        """
        url = f"{self.base_url}/admin/draft-orders"
        payload = {
            "region_id": "reg_01K5V7CVJ7WDWM9KENJ5PSB73H",
            "email": customer_email,
            "billing_address": {
                "first_name": "John",
                "last_name": "Doe",
                "address_1": "123 Main St",
                "city": "New York",
                "country_code": "US",
                "postal_code": "10001",
            },
            "shipping_address": {
                "first_name": "John",
                "last_name": "Doe",
                "address_1": "123 Main St",
                "city": "New York",
                "country_code": "US",
                "postal_code": "10001",
            },
            "items": [
                {"variant_id": variant_id, "quantity": int(quantity)}
                for variant_id, quantity in zip(variant_ids, quantities)
            ],
        }

        response = requests.post(url, headers=self._get_headers(), json=payload)
        return response.json()
