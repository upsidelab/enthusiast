import logging
import json
from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.structures import Address, ProductDetails, ProductUpdateDetails

from .medusa_product_source import MedusaProductSource
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

    def get_product_by_sku(self, sku: str) -> ProductDetails | None:
        # On Medusa side, variants do have "sku" field, but it is not possible to filter products by that field.
        # The reason for this is that Medusa treats the SKU as an internal-purpose identifier, whereas the EAN is
        # treated as an external one. That is why EAN is treated as a counterpart of the of SKU on the Medusa side.
        params = { "variants[ean][]": sku }
        response = self._client.get("/admin/products", params=params)
        products_data = response.get("products", [])

        if len(products_data) == 0:
            return None

        return MedusaProductSource.get_product(products_data[0])


    def create_product(self, product_details: ProductDetails) -> str:
        variant_options = self._parse_properties_to_variant_options(product_details.properties)

        payload = {
            "title": product_details.name,
            "description": product_details.description,
            "handle": product_details.slug,
            "options":
                self._parse_variant_options_to_product_options(variant_options)
                if variant_options else
                self._default_product_options(),
            "variants": [
                {
                    "title": product_details.name,
                    # SKU persisted as EAN on Medusa side. See the comment in get_product_by_sku for details.
                    "ean": product_details.sku,
                    "prices": [
                        {
                            "currency_code": self._get_default_store_currency_code(),
                            "amount": product_details.price,
                        }
                    ]
                }
            ],
        }

        if variant_options:
            payload["variants"][0]["options"] = variant_options

        response = self._client.post("/admin/products", payload)
        return response["product"]["id"]

    def update_product(self, sku: str, product_details: ProductUpdateDetails) -> bool:
        product_details_before_update = self.get_product_by_sku(sku)

        if not product_details_before_update:
            return False

        def remove_none_values(d: dict) -> dict:
            return {k: v for k, v in d.items() if v is not None}

        variant_id = self._get_default_variant_id_for_product_id(product_details_before_update.entry_id)
        variant_options = self._parse_properties_to_variant_options(product_details.properties)

        payload = remove_none_values({
            "title": product_details.name,
            "description": product_details.description,
            "handle": product_details.slug,
            "options": self._parse_variant_options_to_product_options(variant_options) if variant_options else None
        })

        variant = remove_none_values({
            "id": variant_id,
            "title": product_details.name,
            "options": variant_options,
            # SKU persisted as EAN on Medusa side. See the comment in get_product_by_sku for details.
            "ean": product_details.sku,
            "prices": (
                [{
                    "currency_code": self._get_default_store_currency_code(),
                    "amount": product_details.price,
                }]
                if product_details.price is not None
                else None
            ),
        })

        if len(variant) > 1:
            payload["variants"] = [variant]

        if len(payload) == 0:
            return False

        self._client.post(f"/admin/products/{product_details_before_update.entry_id}", payload)
        return True


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

    @staticmethod
    def _parse_properties_to_variant_options(properties: str):
        # ProductDetails.properties is expected to be a JSON string (e.g. '{"property": "value"}').
        # If parsing fails, the connector assumes there are no properties to create or update.
        try:
            return json.loads(properties) if properties else None
        except (TypeError, json.JSONDecodeError):
            return None

    @staticmethod
    def _parse_variant_options_to_product_options(variant_options: dict[str, str]) -> list[dict[str, str | list[str]]]:
        return [ {"title": property_name, "values": [value] } for property_name, value in variant_options.items() ]

    @staticmethod
    def _default_product_options() -> list[dict[str, str | list[str]]]:
        return [{ "title": "Default", "values": ["Default"] }]
