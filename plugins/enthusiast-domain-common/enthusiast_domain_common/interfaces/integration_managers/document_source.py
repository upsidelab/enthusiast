from abc import ABC

from suvereo_common.integrations import BaseSourceIntegrationManager


class BaseDocumentSourceManager(BaseSourceIntegrationManager, ABC):
    """Abstract manager for integrations that fetch documents from an external source."""
