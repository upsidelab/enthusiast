import json
import logging
from typing import List

from enthusiast_common.tools import BaseLLMTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


StockUpdateMemoryEntry = dict[str, bool]


class StockUpdateItem(BaseModel):
    sku: str = Field(description="Product SKU from the invoice line item")
    quantity: int = Field(description="Quantity to add to current stock.")


class StockUpdateBatchInput(BaseModel):
    items: List[StockUpdateItem] = Field(description="List of SKU/quantity pairs to update")


class UpdateStockLevelsTool(BaseLLMTool):
    """Validates SKUs against the catalog and updates stock levels in a single batch call."""

    NAME = "update_stock_levels"
    DESCRIPTION = (
        "Tool for updating stock levels for products based on SKUs and quantities extracted from an invoice. "
        "Reports success or failure per SKU without failing the entire batch."
    )
    ARGS_SCHEMA = StockUpdateBatchInput
    RETURN_DIRECT = False

    def run(self, items: List[StockUpdateItem]) -> str:
        connector = self._injector.ecommerce_platform_connector

        if not connector:
            self._injector.tool_scratchpad.record(self.NAME, {item.sku: False for item in items})
            return "No eCommerce connector is configured. Cannot update stock levels."

        response = {}
        success_map: StockUpdateMemoryEntry = {}

        for item in items:
            try:
                success = connector.update_stock(item.sku, item.quantity)
                response[item.sku] = "Stock updated successfully" if success else "Failed to update stock"
                success_map[item.sku] = success
            except Exception as e:
                logger.error("Failed to update stock for SKU %s: %s", item.sku, e)
                response[item.sku] = f"Error: {e}"
                success_map[item.sku] = False

        self._injector.tool_scratchpad.record(self.NAME, success_map)
        return json.dumps(response)
