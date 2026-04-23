import json
from unittest.mock import MagicMock

import pytest

from enthusiast_agent_invoice_scanning.tools.update_stock_levels_tool import (
    StockUpdateItem,
    UpdateStockLevelsTool,
)
from enthusiast_common.structures import ProductDetails


@pytest.fixture
def injector():
    mock = MagicMock()
    mock.ecommerce_platform_connector = MagicMock()
    return mock


@pytest.fixture
def tool(injector):
    return UpdateStockLevelsTool(data_set_id=1, llm=MagicMock(), injector=injector)


def test_returns_no_connector_message_when_connector_is_none():
    injector = MagicMock()
    injector.ecommerce_platform_connector = None
    tool = UpdateStockLevelsTool(data_set_id=1, llm=MagicMock(), injector=injector)

    result = tool.run([StockUpdateItem(sku="SKU-001", quantity=10)])

    assert "no ecommerce connector" in result.lower()


def test_warns_about_unknown_sku(tool, injector):
    injector.ecommerce_platform_connector.get_product_by_sku.return_value = None

    result = json.loads(tool.run([StockUpdateItem(sku="UNKNOWN", quantity=5)]))

    assert "not found" in result["UNKNOWN"].lower()
    injector.ecommerce_platform_connector.update_stock.assert_not_called()


def test_updates_stock_for_known_sku(tool, injector):
    fake_product = ProductDetails(
        entry_id="prod_1", name="Widget", slug="widget",
        description="", sku="SKU-001", properties="", categories="", price=9.99,
    )
    injector.ecommerce_platform_connector.get_product_by_sku.return_value = fake_product
    injector.ecommerce_platform_connector.update_stock.return_value = True

    result = json.loads(tool.run([StockUpdateItem(sku="SKU-001", quantity=42)]))

    assert result["SKU-001"] == "Stock updated successfully"
    injector.ecommerce_platform_connector.update_stock.assert_called_once_with("SKU-001", 42)


def test_handles_mixed_known_and_unknown_skus(tool, injector):
    fake_product = ProductDetails(
        entry_id="prod_1", name="Widget", slug="widget",
        description="", sku="SKU-001", properties="", categories="", price=9.99,
    )

    def get_product(sku):
        return fake_product if sku == "SKU-001" else None

    injector.ecommerce_platform_connector.get_product_by_sku.side_effect = get_product
    injector.ecommerce_platform_connector.update_stock.return_value = True

    result = json.loads(
        tool.run([
            StockUpdateItem(sku="SKU-001", quantity=10),
            StockUpdateItem(sku="GHOST", quantity=5),
        ])
    )

    assert result["SKU-001"] == "Stock updated successfully"
    assert "not found" in result["GHOST"].lower()


def test_handles_connector_exception(tool, injector):
    fake_product = ProductDetails(
        entry_id="prod_1", name="Widget", slug="widget",
        description="", sku="SKU-001", properties="", categories="", price=9.99,
    )
    injector.ecommerce_platform_connector.get_product_by_sku.return_value = fake_product
    injector.ecommerce_platform_connector.update_stock.side_effect = Exception("Medusa down")

    result = json.loads(tool.run([StockUpdateItem(sku="SKU-001", quantity=10)]))

    assert "error" in result["SKU-001"].lower()
