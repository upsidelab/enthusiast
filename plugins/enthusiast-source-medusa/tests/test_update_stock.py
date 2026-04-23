from unittest.mock import MagicMock
import pytest

from enthusiast_source_medusa.medusa_platform_connector import MedusaPlatformConnector


@pytest.fixture
def connector():
    return MedusaPlatformConnector(
        base_url="http://medusa:9000",
        admin_base_url="http://medusa:9000",
        api_key="test-key",
    )


def test_update_stock_returns_false_when_sku_not_found(connector):
    connector.get_product_by_sku = MagicMock(return_value=None)

    result = connector.update_stock("UNKNOWN-SKU", 50)

    assert result is False


def test_update_stock_calls_api_and_returns_true(connector):
    from enthusiast_common.structures import ProductDetails

    fake_product = ProductDetails(
        entry_id="prod_123",
        name="Test",
        slug="test",
        description="",
        sku="SKU-001",
        properties="",
        categories="",
        price=0.0,
    )
    connector.get_product_by_sku = MagicMock(return_value=fake_product)
    connector._get_default_variant_id_for_product_id = MagicMock(return_value="var_456")
    connector._get_inventory_item_id_for_variant = MagicMock(return_value="invitem_789")
    connector._get_default_stock_location_id = MagicMock(return_value="sloc_abc")
    connector._client.post = MagicMock(return_value={})

    result = connector.update_stock("SKU-001", 50)

    assert result is True
    connector._client.post.assert_called_once_with(
        "/admin/inventory-items/invitem_789/stock-locations/sloc_abc",
        {"stocked_quantity": 50},
    )


def test_update_stock_raises_when_no_inventory_item(connector):
    from enthusiast_common.structures import ProductDetails
    from enthusiast_common.errors import ECommerceConnectorError

    fake_product = ProductDetails(
        entry_id="prod_123",
        name="Test",
        slug="test",
        description="",
        sku="SKU-001",
        properties="",
        categories="",
        price=0.0,
    )
    connector.get_product_by_sku = MagicMock(return_value=fake_product)
    connector._get_default_variant_id_for_product_id = MagicMock(return_value="var_456")
    connector._client.get = MagicMock(return_value={"variant": {"inventory_items": []}})
    connector._get_default_stock_location_id = MagicMock(return_value="sloc_abc")

    with pytest.raises(ECommerceConnectorError, match="no inventory items"):
        connector.update_stock("SKU-001", 50)


def test_update_stock_raises_when_no_stock_location(connector):
    from enthusiast_common.structures import ProductDetails
    from enthusiast_common.errors import ECommerceConnectorError

    fake_product = ProductDetails(
        entry_id="prod_123",
        name="Test",
        slug="test",
        description="",
        sku="SKU-001",
        properties="",
        categories="",
        price=0.0,
    )
    connector.get_product_by_sku = MagicMock(return_value=fake_product)
    connector._get_default_variant_id_for_product_id = MagicMock(return_value="var_456")
    connector._get_inventory_item_id_for_variant = MagicMock(return_value="invitem_789")
    connector._client.get = MagicMock(return_value={"stock_locations": []})

    with pytest.raises(ECommerceConnectorError, match="No stock locations"):
        connector.update_stock("SKU-001", 50)
