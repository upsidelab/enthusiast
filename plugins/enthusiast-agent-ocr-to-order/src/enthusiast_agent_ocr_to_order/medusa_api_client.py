import base64
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MedusaAPIClient:
    BASE_URL = settings.MEDUSA_BASE_URL
    encoded_api_key_bytes = base64.b64encode(settings.MEDUSA_API_KEY.encode("utf-8"))
    encoded_api_key = encoded_api_key_bytes.decode("utf-8")
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_api_key}",
    }

    def list_regions(self) -> list[dict]:
        """
        Fetch all regions from Medusa admin API.
        Each region includes id, name, currency, tax info, etc.
        """
        try:
            url = f"{self.BASE_URL}/admin/regions"
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            data = response.json()
            return data.get("regions", [])
        except Exception as e:
            logger.error("Error fetching regions: %s", e)
            return []

    def get_variants(self, product_id: str):
        """
        Fetch all variants for a given product.
        """
        try:
            url = f"{self.BASE_URL}/admin/products/{product_id}"
            response = requests.get(url, headers=self.HEADERS)
            return response.json()
        except Exception as e:
            logger.error(e)

    def create_admin_order(self, customer_email: str, variant_ids: list[str], quantities: list[str]) -> dict:
        """
        Create an admin draft order.
        """
        url = f"{self.BASE_URL}/admin/draft-orders"
        payload = {
            "region_id": self.list_regions()[0]["id"],
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

        response = requests.post(url, headers=self.HEADERS, json=payload)
        return response.json()
