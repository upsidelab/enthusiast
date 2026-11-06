from abc import abstractmethod

from suvereo_common.integrations import BaseIntegration

from enthusiast_domain_common.connectors import ECommercePlatformConnector
from enthusiast_domain_common.interfaces.integration_managers import BaseECommerceIntegrationManager
from enthusiast_domain_common.interfaces.integrations.product_source import ProductSourcePlugin


class ECommerceIntegrationPlugin(BaseIntegration):
    """A BaseIntegration that provides a platform connector and a product data source."""

    INTEGRATION_TYPE_NAME = "E-Commerce system"
    INTEGRATION_MANAGER = BaseECommerceIntegrationManager

    @abstractmethod
    def build_connector(self) -> ECommercePlatformConnector:
        """Return a connector for the e-commerce platform this integration manages."""

    @abstractmethod
    def build_product_source(self) -> ProductSourcePlugin:
        """Return a ProductSourcePlugin configured with this integration's credentials."""
