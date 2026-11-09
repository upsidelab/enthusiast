from abc import ABC

from suvereo_common.integrations import BaseSourceIntegrationManager


class BaseProductSourceManager(BaseSourceIntegrationManager, ABC):
    """Abstract manager for integrations that fetch products from an external source."""
