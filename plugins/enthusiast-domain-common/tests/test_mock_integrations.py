import pytest
from enthusiast_domain_common import ECommerceIntegrationPlugin
from enthusiast_domain_common.evaluation import DocumentMockIntegration, ECommerceMockIntegration
from suvereo_common.evaluation.mocks import MockConfigError
from suvereo_common.evaluation.trace import TraceRecorder


def _configured(integration_class, base_dir=None, **config):
    integration = integration_class()
    integration.set_runtime_arguments({"configuration_args": config})
    if base_dir is not None:
        integration.base_dir = base_dir
    return integration


class TestECommerceMockIntegration:
    def test_is_an_e_commerce_integration(self):
        assert issubclass(ECommerceMockIntegration, ECommerceIntegrationPlugin)

    def test_one_catalog_file_feeds_both_the_product_source_and_the_connector(self, tmp_path):
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "products.yaml").write_text("- {sku: SKU-1, name: Red Mug, price: 12.5}\n")
        integration = _configured(ECommerceMockIntegration, tmp_path, data={"catalog": "data/products.yaml"})

        synced = integration.build_product_source().fetch()

        assert [p.sku for p in synced] == ["SKU-1"]
        assert integration.build_connector().get_product_by_sku("SKU-1").price == 12.5

    def test_a_csv_catalog_is_read_too(self, tmp_path):
        (tmp_path / "products.csv").write_text("sku,name,price,stock\nSKU-1,Red Mug,12.5,4\n")
        integration = _configured(ECommerceMockIntegration, tmp_path, data={"catalog": "products.csv"})

        connector = integration.build_connector()

        assert (connector.get_product_by_sku("SKU-1").price, connector.stock["SKU-1"]) == (12.5, 4)

    def test_blank_csv_cells_take_the_defaults(self, tmp_path):
        (tmp_path / "products.csv").write_text("sku,name,price,stock\nSKU-1,Red Mug,,\n")
        integration = _configured(ECommerceMockIntegration, tmp_path, data={"catalog": "products.csv"})

        [product] = integration.build_product_source().fetch()

        assert (product.price, integration.build_connector().stock["SKU-1"]) == (0.0, 0)

    def test_a_short_csv_row_takes_the_defaults(self, tmp_path):
        (tmp_path / "products.csv").write_text("sku,name,price,stock\nSKU-1,Red Mug\n")
        integration = _configured(ECommerceMockIntegration, tmp_path, data={"catalog": "products.csv"})

        assert integration.build_product_source().fetch()[0].price == 0.0

    def test_an_invalid_catalog_is_reported_when_syncing_too(self):
        integration = _configured(ECommerceMockIntegration, data={"catalog": [{"name": "no sku"}]})

        with pytest.raises(MockConfigError, match="Invalid catalog product"):
            integration.build_product_source()

    def test_the_connector_is_shared_and_records_into_the_run_trace(self):
        integration = _configured(ECommerceMockIntegration, data={"catalog": [{"sku": "SKU-1", "name": "Mug"}]})
        integration.recorder = recorder = TraceRecorder()

        integration.build_connector().create_order_with_items([("SKU-1", 1)])

        assert integration.build_connector() is integration.mock
        assert [c.method for c in recorder.trace.mock_calls] == ["create_order_with_items"]

    def test_a_missing_catalog_file_is_reported(self, tmp_path):
        integration = _configured(ECommerceMockIntegration, tmp_path, data={"catalog": "nope.yaml"})

        with pytest.raises(MockConfigError, match="nope.yaml"):
            integration.build_connector()


class TestDocumentMockIntegration:
    def test_fetches_fixture_documents(self, tmp_path):
        (tmp_path / "manuals.yaml").write_text(
            "- {url: https://docs/kettle, title: Kettle manual, content: Descale monthly.}\n"
        )
        integration = _configured(DocumentMockIntegration, tmp_path, data={"documents": "manuals.yaml"})

        assert [d.title for d in integration.fetch()] == ["Kettle manual"]

    @pytest.mark.parametrize(
        "config, message",
        [
            ({"data": {"documents": [{"url": "x"}]}}, "Invalid fixture document"),
            ({"behaviour": {"fetch": {"returns": []}}}, "fetch"),
        ],
    )
    def test_invalid_configuration_is_reported(self, config, message):
        integration = _configured(DocumentMockIntegration, **config)

        with pytest.raises(MockConfigError, match=message):
            integration.fetch()
