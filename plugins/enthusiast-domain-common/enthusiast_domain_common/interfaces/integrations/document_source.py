from abc import abstractmethod

from suvereo_common.integrations import BaseIntegration

from enthusiast_domain_common.interfaces.integration_managers import BaseDocumentSourceManager
from enthusiast_domain_common.structures import DocumentDetails


class DocumentSourcePlugin(BaseIntegration):
    """Fetches documents from an external source.

    Subclasses must declare ``TYPE``, ``NAME``, and implement ``fetch()``.
    Persistence is handled by the domain definition's ``DocumentSourceManager``.
    """

    INTEGRATION_TYPE_NAME = "Document source"
    INTEGRATION_MANAGER = BaseDocumentSourceManager

    @abstractmethod
    def fetch(self) -> list[DocumentDetails]:
        """Return all documents available from this source."""
