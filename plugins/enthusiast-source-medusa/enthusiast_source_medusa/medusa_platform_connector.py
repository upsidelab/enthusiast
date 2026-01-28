import logging
from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.structures import Address, ProductDetails

from .medusa_api_client import MedusaAPIClient

logger = logging.getLogger(__name__)

DEFAULT_EMAIL = "test@example.com"
DEFAULT_ADDRESS = Address(
    first_name="Dummy",
    last_name="Customer",
    address_line1="200 5th Avenue",
    city="New York",
    postal_code="10001",
    country_code="US",
)

class MedusaPlatformConnector(ECommercePlatformConnector):
    def __init__(self, base_url: str, admin_base_url: str, api_key: str, region_id: Optional[str] = None):
        self._client = MedusaAPIClient(base_url, api_key)
        self._base_url = base_url.rstrip("/")
        self._admin_base_url = admin_base_url.rstrip("/")
        self._region_id = region_id

    def create_empty_order(self, email: Optional[str] = None, address: Optional[Address] = None) -> str:
        raise NotImplementedError

    def add_to_order(self, order_id: str, sku: str, quantity: int) -> bool:
        raise NotImplementedError

    def create_order_with_items(self, items: list[tuple[str, int]], email: Optional[str] = None, address: Optional[Address] = None) -> str:
        email_or_default = email or DEFAULT_EMAIL
        address_or_default = address or DEFAULT_ADDRESS

        payload = {
            "region_id": self._get_default_region_id(),
            "email": email_or_default,
            "billing_address": self._address_to_payload_dict(address_or_default),
            "shipping_address": self._address_to_payload_dict(address_or_default),
            "items": [
                {"variant_id": self._get_default_variant_id_for_product_id(product_id), "quantity": int(quantity)}
                for product_id, quantity in items
            ]
        }
        response = self._client.post("/admin/draft-orders", payload)
        return response["draft_order"]["id"]

    def get_product_by_sku(self, sku: str) -> ProductDetails:
        raise NotImplementedError

    def create_product(self, product_details: ProductDetails) -> str:
        payload = {
            "title": product_details.name,
            "description": product_details.description,
            "handle": product_details.slug,
            "options": [{
                "title": "Default",
                "values": ["Default"],
            }],
            "variants": [
                {
                    "title": product_details.name,
                    "sku": product_details.sku,
                    "prices": [
                        {
                            "currency_code": self._get_default_store_currency_code(),
                            "amount": product_details.price,
                        }
                    ]
                }
            ],
            "external_id": product_details.entry_id,
        }

        response = self._client.post("/admin/products", payload)
        return response["product"]["id"]

    def update_product(self, sku: str, product_details: ProductDetails) -> bool:
        raise NotImplementedError

    def get_admin_url_for_order_id(self, order_id: str) -> str:
        return f"{self._admin_base_url}/app/draft-orders/{order_id}"

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

        return { key: value for key, value in payload.items() if value is not None }

    def _get_default_variant_id_for_product_id(self, product_id: str) -> str:
        return self._client.get(f"/admin/products/{product_id}")["product"]["variants"][0]["id"]

    def _get_default_store_currency_code(self) -> str:
        store_data = self._get_default_store_data()
        default_currency = next(
            (currency for currency in store_data['supported_currencies'] if currency.get("is_default") is True),
            None
        )
        return default_currency["currency_code"]

    def _get_default_store_data(self):
        return self._client.get("/admin/stores")["stores"][0]
