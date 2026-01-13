import base64
import logging
from typing import Any, Optional

import requests

from .base_ecommerce_platform_connector import BaseECommercePlatformConnector
from .. import ProductDetails
from ..structures import Address


# TODO move to Medusa's package

class MedusaAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._headers = self._build_headers(api_key)

    def get(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        response = requests.get(url, data=body, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, body: dict[str, Any] = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        response = requests.post(url, data=body, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def _build_headers(self, api_key: str) -> dict[str, str]:
        encoded_api_key_bytes = base64.b64encode(api_key.encode("utf-8"))
        encoded_api_key = encoded_api_key_bytes.decode("utf-8")
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_api_key}",
        }

logger = logging.getLogger(__name__)

DEFAULT_EMAIL = "test@example.com"
DEFAULT_ADDRESS = Address(
    first_name="John",
    last_name="Doe",
    address_line1="200 5th Avenue",
    city="New York",
    postal_code="10001",
    country_code="US",
)

class MedusaPlatformConnector(BaseECommercePlatformConnector):
    def __init__(self, base_url: str, api_key: str, region_id: Optional[str] = None):
        self._client = MedusaAPIClient(base_url, api_key)
        self._region_id = region_id

    def create_empty_order(self) -> str:
        raise NotImplementedError

    def add_to_order(self, order_id: str, sku: str, quantity: int) -> bool:
        raise NotImplementedError

    def create_order_with_items(self, items: list[tuple[str, int]], email: Optional[str], address: Optional[Address]) -> str:
        email_or_default = email or DEFAULT_EMAIL
        address_or_default = address or DEFAULT_ADDRESS

        payload = {
            "region_id": self._get_default_region_id(),
            "email": email_or_default,
            "billing_address": self._address_to_payload_dict(address_or_default),
            "shipping_address": self._address_to_payload_dict(address_or_default),
            "items": [
                {"variant_id": variant_id, "quantity": int(quantity)}
                for variant_id, quantity in items
            ]
        }
        response = self._client.post("/admin/draft-orders", payload)
        return response["id"]

    def get_product_by_sku(self, sku: str) -> ProductDetails:
        raise NotImplementedError

    def create_product(self, product_details: ProductDetails) -> bool:
        raise NotImplementedError

    def update_product(self, sku: str, product_details: ProductDetails) -> bool:
        raise NotImplementedError

    def _get_region_id_or_default(self) -> str:
        if self._region_id:
            return self._region_id

        return self._get_default_region_id()

    def _get_default_region_id(self) -> str:
        response = self._client.get("/admin/regions")
        regions = response.get("regions", [])
        if not regions:
            logger.error("No regions configured in Medusa. Fix your Medusa configuration to allow placing orders.")

        return regions[0]["id"]

    def _address_to_payload_dict(self, address: Address) -> dict[str, str]:
        payload = {
            "first_name": address.first_name,
            "last_name": address.last_name,
            "address_1": address.address_line1,
            "address_2": address.address_line2,
            "city": address.city,
            "country_code": address.country_code,
            "postal_code": address.postal_code,
            "province": address.state_or_province,
            "phone": address.phone_number,
            "company": address.company,
        }

        return { key: value for key, value in payload if value is not None }
