import json
import logging
from typing import Optional

from enthusiast_common.connectors import ECommercePlatformConnector
from enthusiast_common.errors import ECommerceConnectorError
from enthusiast_common.structures import Address, ProductDetails, ProductUpdateDetails

from .medusa_api_client import MedusaAPIClient
from .medusa_product_source import MedusaProductSource

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

    required_product_create_fields = { 'name', 'sku', 'price' }

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
        try:
            return response["draft_order"]["id"]
        except (KeyError, TypeError):
            raise ECommerceConnectorError(f"Medusa returned an unexpected response when creating the draft order: {response}")

    def get_product_by_sku(self, sku: str) -> Optional[ProductDetails]:
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
        self._validate_create_product_data(product_details)
        variant_options = self._parse_properties_to_variant_options(product_details.properties)

        payload = self._remove_none_values({
            "title": product_details.name,
            "description": product_details.description,
            "handle": product_details.slug,
            "options": self._parse_variant_options_to_product_options(variant_options)
            if variant_options else
            self._default_product_options()
        })

        variant = self._remove_none_values({
            "title": product_details.name,
            "options": variant_options,
            # SKU persisted as EAN on Medusa side. See the comment in get_product_by_sku for details.
            "ean": product_details.sku,
            # Also set as sku so the auto-created inventory item inherits it. See _get_inventory_item_id_by_sku.
            "sku": product_details.sku,
            "prices": (
                [{
                    "currency_code": self._get_default_store_currency_code(),
                    "amount": product_details.price,
                }]
                if product_details.price is not None
                else None
            ),
        })

        payload["variants"] = [variant]

        response = self._client.post("/admin/products", payload)
        try:
            return response["product"]["id"]
        except (KeyError, TypeError):
            raise ECommerceConnectorError(f"Medusa returned an unexpected response when creating the product: {response}")

    def update_product(self, sku: str, product_details: ProductUpdateDetails) -> bool:
        product_details_before_update = self.get_product_by_sku(sku)

        if not product_details_before_update:
            return False

        variant_id = self._get_default_variant_id_for_product_id(product_details_before_update.entry_id)
        variant_options = self._parse_properties_to_variant_options(product_details.properties)

        payload = self._remove_none_values({
            "title": product_details.name,
            "description": product_details.description,
            "handle": product_details.slug,
            "options": self._parse_variant_options_to_product_options(variant_options) if variant_options else None
        })

        variant = self._remove_none_values({
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

    def update_stock(self, sku: str, quantity: int) -> bool:
        """Add quantity to the stocked quantity for a product variant identified by SKU.

        Fetches the current stocked_quantity and adds the given quantity to it,
        so that invoices accumulate stock rather than overwrite it.

        Returns True if updated, False if the SKU was not found.
        """
        product = self.get_product_by_sku(sku)
        if not product:
            return False

        inventory_item_id = self._get_inventory_item_id_by_sku(sku)
        location_id = self._get_default_stock_location_id()

        current_quantity = self._get_stocked_quantity(inventory_item_id, location_id)
        new_quantity = current_quantity + quantity

        self._client.post(
            f"/admin/inventory-items/{inventory_item_id}/location-levels/{location_id}",
            {"stocked_quantity": new_quantity},
        )
        return True

    def _get_stocked_quantity(self, inventory_item_id: str, location_id: str) -> int:
        response = self._client.get(
            f"/admin/inventory-items/{inventory_item_id}/location-levels",
            params={"location_id": location_id},
        )
        levels = response.get("inventory_levels", [])
        if not levels:
            return 0
        return levels[0].get("stocked_quantity", 0)

    def _get_inventory_item_id_by_sku(self, sku: str) -> str:
        # Inventory items can't be queried by variant_id. They inherit the variant's sku
        # field, which we set explicitly at creation time alongside ean for this purpose.
        response = self._client.get("/admin/inventory-items", params={"sku": sku})
        inventory_items = response.get("inventory_items", [])
        if not inventory_items:
            raise ECommerceConnectorError(
                f"No inventory item found for SKU '{sku}'. "
                "Ensure the product variant was created with manage_inventory enabled."
            )
        return inventory_items[0]["id"]

    def _get_default_stock_location_id(self) -> str:
        response = self._client.get("/admin/stock-locations")
        locations = response.get("stock_locations", [])
        if not locations:
            raise ECommerceConnectorError(
                "No stock locations configured in Medusa. At least one stock location must exist to update inventory."
            )
        return locations[0]["id"]

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
            raise ECommerceConnectorError("No regions are configured in Medusa. At least one region must exist to place orders.")
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
        response = self._client.get(f"/admin/products/{product_id}")
        variants = response.get("product", {}).get("variants", [])
        if not variants:
            raise ECommerceConnectorError(f"Product '{product_id}' has no variants and cannot be ordered.")
        return variants[0]["id"]

    def _get_default_store_currency_code(self) -> str:
        store_data = self._get_default_store_data()
        default_currency = next(
            (currency for currency in store_data['supported_currencies'] if currency.get("is_default") is True),
            None
        )
        if default_currency is None:
            raise ECommerceConnectorError("No default currency is configured in Medusa. At least one default currency must exist.")
        return default_currency["currency_code"]

    def _get_default_store_data(self):
        response = self._client.get("/admin/stores")
        try:
            return response["stores"][0]
        except (KeyError, IndexError):
            raise ECommerceConnectorError(f"Medusa returned an unexpected response when fetching store data: {response}")

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

    @staticmethod
    def _remove_none_values(d: dict) -> dict:
        return {k: v for k, v in d.items() if v is not None}
