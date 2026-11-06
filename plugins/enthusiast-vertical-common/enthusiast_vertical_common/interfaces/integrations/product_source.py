from abc import abstractmethod

from suvereo_common.integrations import BaseIntegration

from enthusiast_vertical_common.interfaces.integration_managers import BaseProductSourceManager
from enthusiast_vertical_common.structures import ProductDetails


class ProductSourcePlugin(BaseIntegration):
    """Fetches products from an external source.

    Subclasses must declare ``TYPE``, ``NAME``, and implement ``fetch()``.
    Persistence is handled by the domain definition's ``ProductSourceManager``.
    """

    INTEGRATION_TYPE_NAME = "Product source"
    INTEGRATION_MANAGER = BaseProductSourceManager

    @abstractmethod
    def fetch(self) -> list[ProductDetails]:
        """Return all products available from this source."""
