import json
import logging
from typing import List

from enthusiast_common.injectors import BaseInjector
from enthusiast_common.tools import BaseLLMTool
from langchain_core.language_models import BaseLanguageModel
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StockUpdateItem(BaseModel):
    sku: str = Field(description="Product SKU from the invoice line item")
    quantity: int = Field(description="Quantity from the invoice line item")


class StockUpdateBatchInput(BaseModel):
    items: List[StockUpdateItem] = Field(description="List of SKU/quantity pairs to update")


class UpdateStockLevelsTool(BaseLLMTool):
    """Validates SKUs against the catalog and updates stock levels in a single batch call."""

    NAME = "update_stock_levels"
    DESCRIPTION = (
        "Tool for updating stock levels for products based on SKUs and quantities extracted from an invoice. "
        "Validates each SKU against the catalog and reports any unrecognized SKUs without failing the batch."
    )
    ARGS_SCHEMA = StockUpdateBatchInput
    RETURN_DIRECT = False

    def __init__(self, data_set_id: int, llm: BaseLanguageModel, injector: BaseInjector | None):
        super().__init__(data_set_id=data_set_id, llm=llm, injector=injector)
        self.injector = injector

    def run(self, items: List[StockUpdateItem]) -> str:
        connector = self.injector.ecommerce_platform_connector

        if not connector:
            return "No eCommerce connector is configured. Cannot update stock levels."

        response = {}

        for item in items:
            try:
                product = connector.get_product_by_sku(item.sku)
                if not product:
                    response[item.sku] = f"SKU not found in catalog"
                    continue

                success = connector.update_stock(item.sku, item.quantity)
                response[item.sku] = "Stock updated successfully" if success else "Failed to update stock"
            except Exception as e:
                logger.error("Failed to update stock for SKU %s: %s", item.sku, e)
                response[item.sku] = f"Error: {e}"

        return json.dumps(response)
