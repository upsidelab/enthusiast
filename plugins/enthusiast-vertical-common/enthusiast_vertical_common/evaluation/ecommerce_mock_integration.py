from functools import cached_property
from typing import Any

from suvereo_common.evaluation.mocks import BaseMockIntegration, FixtureRecords

from ..connectors import ECommercePlatformConnector
from ..interfaces import ECommerceIntegrationPlugin
from .catalog_product import CatalogProduct
from .ecommerce_connector_mock import ECommerceConnectorMock
from .fixture_product_source import FixtureProductSource


class ECommerceMockIntegration(BaseMockIntegration, ECommerceIntegrationPlugin):
    """One declaration for a mocked shop: its catalog is both synced for search and served by the connector mock."""

    TYPE = "mock_ecommerce"
    NAME = "Mock e-commerce platform"
    MOCK_CLASS = ECommerceConnectorMock

    def build_connector(self) -> ECommercePlatformConnector:
        return self.mock

    def build_product_source(self) -> FixtureProductSource:
        return FixtureProductSource(
            [product.to_product_details() for product in CatalogProduct.load_all(self._catalog)]
        )

    def _mock_data(self) -> dict[str, Any]:
        return {**self.config.data, "catalog": self._catalog}

    @cached_property
    def _catalog(self) -> list[dict[str, Any]]:
        return FixtureRecords.load(self.config.data.get("catalog"), self.base_dir)
