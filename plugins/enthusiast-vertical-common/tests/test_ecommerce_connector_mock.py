import pytest
from enthusiast_vertical_common import ECommercePlatformConnector, ProductDetails, ProductUpdateDetails
from enthusiast_vertical_common.connectors.errors import ECommerceConnectorError
from enthusiast_vertical_common.evaluation import ECommerceConnectorMock
from suvereo_common.evaluation.mocks import MockConfigError

CATALOG = [
    {"sku": "SKU-1", "name": "Red Mug", "price": 12.5, "stock": 3},
    {"sku": "SKU-2", "name": "Blue Mug"},
]


def _mock(behaviour=None, catalog=CATALOG):
    return ECommerceConnectorMock(behaviour, {"catalog": catalog})


class TestOrders:
    def test_an_order_with_items_keeps_them_under_a_deterministic_id(self):
        mock = _mock()

        first = mock.create_order_with_items([("SKU-1", "2")], email="a@b.c")
        second = mock.create_empty_order()

        assert (first, second) == ("ORD-1", "ORD-2")
        assert mock.orders["ORD-1"] == {"items": [("SKU-1", 2)], "email": "a@b.c", "address": None}

    def test_items_are_added_to_an_existing_order_only_for_known_products(self):
        mock = _mock()
        order_id = mock.create_empty_order()

        assert mock.add_to_order(order_id, "SKU-2", 1) is True
        assert mock.add_to_order(order_id, "SKU-404", 1) is False
        assert mock.add_to_order("ORD-404", "SKU-1", 1) is False
        assert mock.orders[order_id]["items"] == [("SKU-2", 1)]

    def test_ordering_an_unknown_sku_fails_like_a_real_shop(self):
        mock = _mock()

        with pytest.raises(ECommerceConnectorError, match="SKU-404"):
            mock.create_order_with_items([("SKU-1", 1), ("SKU-404", 2)])

        assert mock.orders == {}
        assert mock.calls[0].error.startswith("ECommerceConnectorError")

    def test_without_a_catalog_any_sku_can_be_ordered(self):
        mock = _mock(catalog=[])

        assert mock.add_to_order(mock.create_empty_order(), "ANYTHING", 1) is True

    def test_an_empty_catalog_stays_open_after_a_product_is_created(self):
        mock = _mock(catalog=[])
        mock.create_product(ProductDetails("E-1", "Mug", "mug", "", "SKU-1", "", "", 1.0))

        assert mock.add_to_order(mock.create_empty_order(), "ANYTHING", 1) is True

    def test_reset_returns_to_the_starting_catalog(self):
        mock = _mock()
        mock.create_order_with_items([("SKU-1", 1)])
        mock.update_stock("SKU-1", -3)
        mock.create_product(ProductDetails("E-9", "Green Mug", "green-mug", "", "SKU-9", "", "", 9.0))

        mock.reset()

        assert (mock.orders, mock.stock["SKU-1"], mock.get_product_by_sku("SKU-9")) == ({}, 3, None)
        assert mock.create_empty_order() == "ORD-1"

    def test_the_admin_url_names_the_order(self):
        assert _mock().get_admin_url_for_order_id("ORD-1").endswith("/orders/ORD-1")


class TestProducts:
    def test_products_are_served_from_the_catalog_with_defaults_filled(self):
        product = _mock().get_product_by_sku("SKU-2")

        assert product == ProductDetails(
            entry_id="SKU-2",
            name="Blue Mug",
            slug="blue-mug",
            description="",
            sku="SKU-2",
            properties="",
            categories="",
            price=0.0,
        )
        assert _mock().get_product_by_sku("SKU-404") is None

    def test_stock_and_product_updates_change_the_catalog(self):
        mock = _mock()

        assert mock.update_stock("SKU-1", -2) is True
        assert mock.update_product("SKU-1", ProductUpdateDetails(price=10.0)) is True
        assert mock.update_stock("SKU-404", 1) is False

        assert mock.stock["SKU-1"] == 1
        assert mock.get_product_by_sku("SKU-1").price == 10.0

    def test_renaming_a_sku_moves_its_stock(self):
        mock = _mock()

        assert mock.update_product("SKU-1", ProductUpdateDetails(sku="SKU-1B")) is True

        assert mock.get_product_by_sku("SKU-1") is None
        assert (mock.get_product_by_sku("SKU-1B").name, mock.stock) == ("Red Mug", {"SKU-1B": 3, "SKU-2": 0})

    def test_renaming_onto_an_existing_sku_is_refused(self):
        mock = _mock()

        assert mock.update_product("SKU-1", ProductUpdateDetails(sku="SKU-2", name="Clash")) is False
        assert mock.get_product_by_sku("SKU-2").name == "Blue Mug"

    def test_creating_a_product_whose_sku_exists_fails_like_a_real_shop(self):
        mock = _mock()

        with pytest.raises(ECommerceConnectorError, match="SKU-1 already exists"):
            mock.create_product(ProductDetails("E-1", "Copy", "copy", "", "SKU-1", "", "", 1.0))

        assert mock.get_product_by_sku("SKU-1").name == "Red Mug"

    def test_null_values_take_the_defaults(self):
        mock = _mock(catalog=[{"sku": "SKU-1", "name": "Mug", "description": None, "price": None}])

        assert (mock.get_product_by_sku("SKU-1").description, mock.get_product_by_sku("SKU-1").price) == ("", 0.0)

    def test_numeric_skus_from_yaml_or_json_are_text(self):
        mock = _mock(catalog=[{"sku": 12345, "name": "Mug", "entry_id": 7}])

        assert mock.get_product_by_sku("12345").entry_id == "7"

    def test_a_created_product_can_be_found(self):
        mock = _mock()
        details = ProductDetails("E-9", "Green Mug", "green-mug", "", "SKU-9", "", "", 9.0)

        assert mock.create_product(details) == "E-9"
        assert mock.get_product_by_sku("SKU-9") == details

    def test_an_invalid_catalog_fails_when_the_mock_is_built(self):
        with pytest.raises(MockConfigError, match="catalog"):
            _mock(catalog=[{"name": "no sku"}])


class TestDeclaredBehaviour:
    def test_declared_behaviour_wins_and_can_raise_the_connector_error_by_name(self):
        mock = _mock(
            {
                "create_order_with_items": {
                    "when": {"items": [["SKU-2", 5]]},
                    "raises": {"error": "ECommerceConnectorError", "message": "Out of stock"},
                }
            }
        )

        with pytest.raises(ECommerceConnectorError, match="Out of stock"):
            mock.create_order_with_items([("SKU-2", 5)])
        assert mock.create_order_with_items([("SKU-1", 1)]) == "ORD-1"

    def test_every_call_is_recorded_with_named_arguments(self):
        mock = _mock()

        mock.create_order_with_items([("SKU-1", 2)])

        assert isinstance(mock, ECommercePlatformConnector)
        assert mock.calls_to("create_order_with_items")[0].arguments["items"] == [("SKU-1", 2)]
